from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase, override_settings
from wagtail.models import Site

from wagtailautocomplete.tests.testapp.models import Group, House, Person

User = get_user_model()


class ObjectsViewTestCase(TestCase):
    def test_autocomplete_missing_pks_param(self):
        """The objects view should return a Bad Request response if not
        given the pks parameter.

        """
        response = self.client.get("/autocomplete/objects/")
        assert response.status_code == 400

    def test_target_model_not_found(self):
        """The objects view should return a Bad Request response if not
        given a valid model type.

        """
        response = self.client.get(
            "/autocomplete/objects/", {"pks": "1,2", "type": "<invalid type>"}
        )
        assert response.status_code == 400

    def test_invalid_pks(self):
        """The objects view should return a Bad Request response if not
        given the valid primary keys.

        """
        invalid = "abcde"
        response = self.client.get("/autocomplete/objects/", {"pks": invalid})
        assert response.status_code == 400

    def test_missing_objects(self):
        """The objects view should return a Not Found response if the given pk
            don't have any associated object
        """
        response = self.client.get("/autocomplete/objects/", {"pks": "99"})
        assert response.status_code == 404


class SearchViewTestCase(TestCase):
    def setUp(self):
        self.site = Site.objects.get(is_default_site=True)
        self.root_page = self.site.root_page
        self.target_page1 = Person.objects.create(name="Adam Note")
        self.target_page2 = Person.objects.create(name="Belle Note")
        self.single_page = House(
            name="Autocomplete singly.",
            owner=self.target_page1,
        )
        self.root_page.add_child(instance=self.single_page)
        self.single_page.occupants.add(self.target_page1, self.target_page2)

    def test_target_model_not_found(self):
        """The search view should return a Bad Request response if not
        given a valid model type.

        """
        response = self.client.post(
            "/autocomplete/search/", data={"type": "<invalid type>"})
        self.assertEqual(response.status_code, 400)

    def test_invalid_limit(self):
        """The search view should return Bad Request if not given
        a numeric query limit.

        """
        invalid = "abcde"
        response = self.client.post("/autocomplete/search/", data={"limit": invalid})
        self.assertEqual(response.status_code, 400)

    def test_search_blank_single_exception_ignored(self):
        """The search view should handle a blank exclude clause."""
        response = self.client.post(
            "/autocomplete/search/",
            data={
                "type": "testapp.Person",
                "query": "note",
                "exclude": "",
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['items']), 2)

    def test_search_blank_multi_exceptions_ignored(self):
        """The search view should handle multiple blank exclude clauses."""
        response = self.client.post(
            "/autocomplete/search/",
            data={
                "type": "testapp.Person",
                "query": "note",
                "exclude": ",,,",
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['items']), 2)

    def test_search_valid_exception(self):
        response = self.client.post(
            "/autocomplete/search/",
            data={
                "type": "testapp.Person",
                "query": "note",
                "exclude": "{},102,103".format(self.target_page1.pk),
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['items']), 1)
        self.assertEqual(response.json()['items'][0]['title'], 'Belle Note')

    def test_search_by_default_field(self):
        """By default, a model's title is used."""
        group = Group.objects.create(title="Some Group")
        response = self.client.post(
            "/autocomplete/search/",
            data={"type": "testapp.Group", "query": "some"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(item["pk"] for item in response.json()["items"]),
            {group.pk},
        )

    def test_search_by_autocomplete_search_field(self):
        """
        A model's 'autocomplete_search_field' attribute is used in the search.
        """
        response = self.client.post(
            "/autocomplete/search/",
            data={"type": "testapp.Person", "query": "note"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(item["pk"] for item in response.json()["items"]),
            set([self.target_page1.pk, self.target_page2.pk]),
        )

    @override_settings(
        WAGTAILAUTOCOMPLETE_CUSTOM_FILTER_FIELDS={
            "testapp.House": {"fields": ["name"]},
        },
        WAGTAILAUTOCOMPLETE_CUSTOM_SEARCH_FIELD={"testapp.House": "name"},
    )
    def test_search_by_field_from_setting_field_name(self):
        """
        Search by field from WAGTAILAUTOCOMPLETE_CUSTOM_SEARCH_FIELD setting.
        """
        response = self.client.post(
            "/autocomplete/search/",
            data={"type": "testapp.House", "query": "singly"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(item["pk"] for item in response.json()["items"]),
            {self.single_page.pk},
        )

    @override_settings(
        WAGTAILAUTOCOMPLETE_CUSTOM_FILTER_FIELDS={
            "testapp.House": {"fields": ["name"]},
        },
        WAGTAILAUTOCOMPLETE_CUSTOM_SEARCH_FIELD={
            "testapp.House": lambda house: f"House named {house.name}",
        },
    )
    def test_search_by_field_from_setting_callable(self):
        """
        Search by WAGTAILAUTOCOMPLETE_CUSTOM_SEARCH_FIELD setting callable.
        """
        response = self.client.post(
            "/autocomplete/search/",
            data={"type": "testapp.House", "query": "singly"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(item["pk"] for item in response.json()["items"]),
            {self.single_page.pk},
        )
        self.assertEqual(
            set(item["title"] for item in response.json()["items"]),
            {f"House named {self.single_page.name}"},
        )

    @override_settings(
        WAGTAILAUTOCOMPLETE_CUSTOM_FILTER_FIELDS={
            "testapp.Person": {"fields": ["group"]},
        },
        WAGTAILAUTOCOMPLETE_CUSTOM_SEARCH_FIELD={"testapp.Person": "group"},
    )
    def test_search_autocomplete_search_field_and_setting(self):
        """
        Search when model defines search field in an attribute and a setting.

        When a model defines an autocomplete_search_field attribute and it is
        also in the WAGTAILAUTOCOMPLETE_CUSTOM_SEARCH_FIELD setting, the
        autocomplete_search_field attribute takes precedence.
        """
        response = self.client.post(
            "/autocomplete/search/",
            data={"type": "testapp.Person", "query": "note"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(item["pk"] for item in response.json()["items"]),
            set([self.target_page1.pk, self.target_page2.pk]),
        )


class CreateViewTestCase(TestCase):
    def setUp(self):
        self.superuser = User.objects.create(
            username="testuser", password="unusable", is_superuser=True
        )
        self.adminuser = User.objects.create(
            username="testuser2", password="unusable")
        # Permission to log into the admin, but not to change
        # anything.
        admin_permission = Permission.objects.get(codename="access_admin")
        self.adminuser.user_permissions.add(admin_permission)

    def test_missing_value_param(self):
        """The create view should return a Bad Request response if not
        given the value parameter.

        """
        self.client.force_login(self.superuser)
        response = self.client.post("/admin/autocomplete/create/")
        assert response.status_code == 400

    def test_target_model_not_found(self):
        """The create view should return a Bad Request response if not
        given a valid model type.

        """
        self.client.force_login(self.superuser)
        response = self.client.post(
            "/admin/autocomplete/create/",
            {"value": "a", "type": "<invalid type>"}
        )
        assert response.status_code == 400

    def test_user_lacks_permissions(self):
        """The create view should return a Forbidden response if the user does
        not have create permission for that model.

        """
        self.client.force_login(self.adminuser)
        response = self.client.post(
            "/admin/autocomplete/create/", {"value": "a"})
        assert response.status_code == 403

    def test_autocomplete_create_not_implemented(self):
        """The create view should return a Bad Request response if
        `autocomplete_create` is not implemented on the model requested.

        """
        self.client.force_login(self.superuser)
        response = self.client.post(
            "/admin/autocomplete/create/", {"value": "a"})
        assert response.status_code == 400

    def test_autocomplete_create_raises_validation_error(self):
        """The create view should return a Bad Request response if
        `autocomplete_create` raises a `ValidationError`

        """
        self.client.force_login(self.superuser)
        response = self.client.post(
            "/admin/autocomplete/create/",
            {
                "type": "testapp.Group",
                "value": "a" * 51,
            },
        )
        assert response.status_code == 400
