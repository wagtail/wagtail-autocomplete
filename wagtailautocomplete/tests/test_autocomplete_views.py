from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from wagtail.core.models import Site

from wagtailautocomplete.tests.testapp.models.page_to_page import (
    MultipleAutocompletePage, SingleAutocompletePage, TargetPage)


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


class SearchViewTestCase(TestCase):
    def setUp(self):
        self.site = Site.objects.get(is_default_site=True)
        self.root_page = self.site.root_page
        self.target_page1 = TargetPage(title="target1 cars")
        self.target_page2 = TargetPage(title="target2 cars")
        self.root_page.add_child(instance=self.target_page1)
        self.root_page.add_child(instance=self.target_page2)
        self.single_page = SingleAutocompletePage(
            title="Autocomplete singly.",
            target=self.target_page1,
        )
        self.multi_page = MultipleAutocompletePage(
            title="Autocomplete multiply.",
        )
        self.root_page.add_child(instance=self.single_page)
        self.root_page.add_child(instance=self.multi_page)
        self.multi_page.targets.add(self.target_page1, self.target_page2)

    def test_target_model_not_found(self):
        """The search view should return a Bad Request response if not
        given a valid model type.

        """
        response = self.client.get(
            "/autocomplete/search/", {"type": "<invalid type>"})
        self.assertEqual(response.status_code, 400)

    def test_invalid_limit(self):
        """The search view should return Bad Request if not given
        a numeric query limit.

        """
        invalid = "abcde"
        response = self.client.get("/autocomplete/search/", {"limit": invalid})
        self.assertEqual(response.status_code, 400)

    def test_search_blank_single_exception_ignored(self):
        """The search view should handle a blank exclude clause."""
        response = self.client.get(
            "/autocomplete/search/"
            "?type=testapp.TargetPage"
            "&query=cars"
            "&exclude="
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['items']), 2)

    def test_search_blank_multi_exceptions_ignored(self):
        """The search view should handle multiple blank exclude clauses."""
        response = self.client.get(
            "/autocomplete/search/"
            "?type=testapp.TargetPage"
            "&query=cars"
            "&exclude=,,,"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['items']), 2)

    def test_search_valid_exception(self):
        response = self.client.get(
            "/autocomplete/search/"
            "?type=testapp.TargetPage"
            "&query=cars"
            "&exclude={},102,103".format(self.target_page1.pk)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['items']), 1)
        self.assertEqual(response.json()['items'][0]['title'], 'target2 cars')


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
