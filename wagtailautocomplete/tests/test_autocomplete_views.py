from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission


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
    def test_target_model_not_found(self):
        """The search view should return a Bad Request response if not
        given a valid model type.

        """
        response = self.client.get("/autocomplete/search/", {"type": "<invalid type>"})
        assert response.status_code == 400

    def test_invalid_pks(self):
        """The objects view should return a Bad Request response if not
        given the valid primary keys.

        """
        invalid = "abcde"
        response = self.client.get("/autocomplete/search/", {"limit": invalid})
        assert response.status_code == 400


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
