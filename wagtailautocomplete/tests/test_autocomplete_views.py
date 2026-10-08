from unittest import mock

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.db import connection, models
from django.test import SimpleTestCase, TestCase
from django.test.utils import isolate_apps
from wagtail.models import Site

from wagtailautocomplete.tests.testapp.models import House, Person
from wagtailautocomplete.views import clean_pks

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

    def test_out_of_range_pks(self):
        """The objects view should return a Bad Request response if given
        primary keys too large for the database.

        """
        response = self.client.get("/autocomplete/objects/", {"pks": "9" * 30})
        assert response.status_code == 400

    def test_out_of_range_pks_page_subclass(self):
        """The objects view should return a Bad Request response if given
        primary keys too large for the database for a Page subclass, whose
        primary key links to its parent's.

        """
        response = self.client.get(
            "/autocomplete/objects/", {"pks": "9" * 30, "type": "testapp.TestPage"}
        )
        assert response.status_code == 400

    def test_missing_objects(self):
        """The objects view should return a Not Found response if the given pk
        don't have any associated object
        """
        response = self.client.get("/autocomplete/objects/", {"pks": "99"})
        assert response.status_code == 404

    def test_duplicate_pks(self):
        """The objects view should return each object once when given the
        same primary key more than once, in any spelling.

        """
        person = Person.objects.create(name="Adam Note")
        for pks in [f"{person.pk},{person.pk}", f"{person.pk},0{person.pk}"]:
            response = self.client.get(
                "/autocomplete/objects/", {"pks": pks, "type": "testapp.Person"}
            )
            assert response.status_code == 200, pks
            assert response.json()["items"] == [{"pk": person.pk, "title": "Adam Note"}]


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
            "/autocomplete/search/", data={"type": "<invalid type>"}
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_limit(self):
        """The search view should return Bad Request if not given
        a numeric query limit.

        """
        invalid = "abcde"
        response = self.client.post("/autocomplete/search/", data={"limit": invalid})
        self.assertEqual(response.status_code, 400)

    def test_negative_limit(self):
        """The search view should return Bad Request if given a negative
        query limit.

        """
        response = self.client.post("/autocomplete/search/", data={"limit": "-1"})
        self.assertEqual(response.status_code, 400)

    def test_out_of_range_limit(self):
        """The search view should return Bad Request if given a query limit
        too large for the database.

        """
        response = self.client.post("/autocomplete/search/", data={"limit": "9" * 30})
        self.assertEqual(response.status_code, 400)

    def test_zero_limit(self):
        """The search view should return no results for a query limit of 0."""
        response = self.client.post(
            "/autocomplete/search/",
            data={"type": "testapp.Person", "query": "note", "limit": "0"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["items"], [])

    def test_largest_limit(self):
        """The search view should accept the largest 64-bit limit."""
        response = self.client.post(
            "/autocomplete/search/",
            data={"type": "testapp.Person", "query": "note", "limit": 2**63 - 1},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["items"]), 2)

    def test_limit_just_out_of_range(self):
        """The search view should return Bad Request for a limit one past the
        largest 64-bit integer.

        """
        response = self.client.post("/autocomplete/search/", data={"limit": 2**63})
        self.assertEqual(response.status_code, 400)

    def test_invalid_exclude(self):
        """The search view should return Bad Request if given non-numeric
        primary keys to exclude.

        """
        response = self.client.post(
            "/autocomplete/search/",
            data={"type": "testapp.Person", "exclude": "abcde"},
        )
        self.assertEqual(response.status_code, 400)

    def test_out_of_range_exclude(self):
        """The search view should return Bad Request if given primary keys
        to exclude that are too large for the database.

        """
        response = self.client.post(
            "/autocomplete/search/",
            data={"type": "testapp.Person", "exclude": "9" * 30},
        )
        self.assertEqual(response.status_code, 400)

    def test_search_blank_single_exception_ignored(self):
        """The search view should handle a blank exclude clause."""
        response = self.client.post(
            "/autocomplete/search/",
            data={
                "type": "testapp.Person",
                "query": "note",
                "exclude": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["items"]), 2)

    def test_search_blank_multi_exceptions_ignored(self):
        """The search view should handle multiple blank exclude clauses."""
        response = self.client.post(
            "/autocomplete/search/",
            data={
                "type": "testapp.Person",
                "query": "note",
                "exclude": ",,,",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["items"]), 2)

    def test_search_valid_exception(self):
        response = self.client.post(
            "/autocomplete/search/",
            data={
                "type": "testapp.Person",
                "query": "note",
                "exclude": f"{self.target_page1.pk},102,103",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["items"]), 1)
        self.assertEqual(response.json()["items"][0]["title"], "Belle Note")


class CreateViewTestCase(TestCase):
    def setUp(self):
        self.superuser = User.objects.create(
            username="testuser", password="unusable", is_superuser=True
        )
        self.adminuser = User.objects.create(username="testuser2", password="unusable")
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
            "/admin/autocomplete/create/", {"value": "a", "type": "<invalid type>"}
        )
        assert response.status_code == 400

    def test_user_lacks_permissions(self):
        """The create view should return a Forbidden response if the user does
        not have create permission for that model.

        """
        self.client.force_login(self.adminuser)
        response = self.client.post("/admin/autocomplete/create/", {"value": "a"})
        assert response.status_code == 403

    def test_autocomplete_create_not_implemented(self):
        """The create view should return a Bad Request response if
        `autocomplete_create` is not implemented on the model requested.

        """
        self.client.force_login(self.superuser)
        response = self.client.post("/admin/autocomplete/create/", {"value": "a"})
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


class HashidField(models.AutoField):
    """Stand-in for a hashid field: "h5" in Python is 5 in the database."""

    def to_python(self, value):
        return value

    def get_prep_value(self, value):
        return int(value[1:])


class CustomTypeField(models.IntegerField):
    def get_internal_type(self):
        return "CustomTypeField"


@isolate_apps("wagtailautocomplete.tests.testapp")
class CleanPksTestCase(SimpleTestCase):
    def test_custom_pk_checks_database_value(self):
        """Primary keys that convert to other types are range-checked by the
        value sent to the database.

        """

        class Hashed(models.Model):
            id = HashidField(primary_key=True)

            class Meta:
                app_label = "testapp"

        self.assertEqual(clean_pks(Hashed, ["h5"]), ["h5"])
        with self.assertRaises(ValidationError):
            clean_pks(Hashed, ["h" + "9" * 30])

    def test_unknown_field_type_not_range_checked(self):
        """Field types the database backend doesn't know are left to the
        database. SQLite returns its 64-bit range for any type; other
        backends raise KeyError.

        """

        class CustomType(models.Model):
            id = CustomTypeField(primary_key=True)

            class Meta:
                app_label = "testapp"

        with mock.patch.object(
            connection.ops, "integer_field_range", side_effect=KeyError
        ):
            self.assertEqual(clean_pks(CustomType, ["9" * 30]), [int("9" * 30)])
