from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from wagtail.documents import get_document_model
from wagtail.models import (
    Collection,
    CollectionViewRestriction,
    Page,
    PageViewRestriction,
)
from wagtail.test.routablepage.models import RoutablePageTest

from wagtailautocomplete.tests.testapp.models import Person

User = get_user_model()
Document = get_document_model()


class PublicAllowListTestCase(TestCase):
    def setUp(self):
        Person.objects.create(name="Adam")
        Person.objects.create(name="Belle")

    def search(self, model_label, query=""):
        return self.client.post(
            "/autocomplete/search/", {"type": model_label, "query": query}
        )

    def objects(self, model_label, pks):
        return self.client.get(
            "/autocomplete/objects/",
            {"type": model_label, "pks": ",".join(map(str, pks))},
        )

    def test_model_not_in_allow_list(self):
        user = User.objects.create(username="admin")
        self.assertEqual(self.search("auth.User", "admin").status_code, 400)
        self.assertEqual(self.objects("auth.User", [user.pk]).status_code, 400)

    def test_admin_urls_ignore_allow_list(self):
        self.client.force_login(User.objects.create_superuser("admin", "", "password"))
        response = self.client.post(
            "/admin/autocomplete/search/", {"type": "testapp.Person", "query": ""}
        )
        self.assertEqual(len(response.json()["items"]), 2)


class PublicPageTestCase(TestCase):
    def setUp(self):
        root = Page.objects.get(depth=1)
        self.public = root.add_child(instance=Page(title="Public page"))
        self.draft = root.add_child(instance=Page(title="Draft page", live=False))
        self.private = root.add_child(instance=Page(title="Private page"))
        self.private_child = self.private.add_child(
            instance=Page(title="Private child page")
        )
        PageViewRestriction.objects.create(
            page=self.private, restriction_type=PageViewRestriction.LOGIN
        )

    def search_titles(self):
        response = self.client.post("/autocomplete/search/", {"query": "page"})
        return {item["title"] for item in response.json()["items"]}

    def test_search_excludes_drafts_and_private_pages(self):
        self.assertEqual(self.search_titles(), {"Public page"})

    def test_search_includes_private_pages_when_restriction_satisfied(self):
        self.client.force_login(User.objects.create_user("user"))
        self.assertEqual(
            self.search_titles(), {"Public page", "Private page", "Private child page"}
        )

    def test_objects_excludes_drafts_and_private_pages(self):
        for page, status in [
            (self.public, 200),
            (self.draft, 404),
            (self.private, 404),
            (self.private_child, 404),
        ]:
            with self.subTest(page=page.title):
                response = self.client.get("/autocomplete/objects/", {"pks": page.pk})
                self.assertEqual(response.status_code, status)


class PublicPageSubclassTestCase(TestCase):
    def setUp(self):
        root = Page.objects.get(depth=1)
        self.public_article = root.add_child(
            instance=RoutablePageTest(title="Public article")
        )
        private = root.add_child(instance=RoutablePageTest(title="Private article"))
        PageViewRestriction.objects.create(
            page=private, restriction_type=PageViewRestriction.LOGIN
        )

    def search(self, model_label):
        return self.client.post(
            "/autocomplete/search/", {"type": model_label, "query": "article"}
        )

    def test_drafts_excluded_with_custom_queryset_filter(self):
        """Drafts are excluded even when a model defines its own
        autocomplete_custom_queryset_filter."""
        Page.objects.get(depth=1).add_child(
            instance=RoutablePageTest(title="Draft article", live=False)
        )
        custom_filter = classmethod(
            lambda cls, search_query, request: cls.objects.filter(
                title__icontains=search_query
            )
        )
        with mock.patch.object(
            RoutablePageTest,
            "autocomplete_custom_queryset_filter",
            custom_filter,
            create=True,
        ):
            response = self.search("routablepagetests.RoutablePageTest")
        self.assertEqual(
            [item["title"] for item in response.json()["items"]], ["Public article"]
        )


class PublicDocumentTestCase(TestCase):
    def setUp(self):
        root = Collection.get_first_root_node()
        private = root.add_child(name="Private")
        private_child = private.add_child(name="Private child")
        CollectionViewRestriction.objects.create(
            collection=private, restriction_type=CollectionViewRestriction.LOGIN
        )
        Document.objects.create(title="Public doc", file="public.txt", collection=root)
        Document.objects.create(
            title="Private doc", file="private.txt", collection=private
        )
        Document.objects.create(
            title="Private child doc",
            file="private_child.txt",
            collection=private_child,
        )

    def search_titles(self):
        response = self.client.post(
            "/autocomplete/search/", {"type": "wagtaildocs.Document", "query": "doc"}
        )
        return {item["title"] for item in response.json()["items"]}

    def test_search_excludes_restricted_collections(self):
        self.assertEqual(self.search_titles(), {"Public doc"})

    def test_search_includes_restricted_collections_when_restriction_satisfied(self):
        self.client.force_login(User.objects.create_user("user"))
        self.assertEqual(
            self.search_titles(), {"Public doc", "Private doc", "Private child doc"}
        )
