from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured
from django.test import RequestFactory, TestCase, override_settings
from wagtail.models import Page, PageViewRestriction
from wagtail.test.routablepage.models import (
    RoutablePageTest,
    RoutablePageWithOverriddenIndexRouteTest,
)

from wagtailautocomplete.allowed import live_pages
from wagtailautocomplete.tests.testapp.models import Person
from wagtailautocomplete.views import (
    WAGTAILAUTOCOMPLETE_ALLOW_PUBLIC_MODELS_DEFAULT,
    apply_allow_rules,
    get_model,
    get_public_rules,
)

User = get_user_model()


def allow_all(queryset, request):
    return queryset


def make_request(user=None):
    request = RequestFactory().get("/")
    request.user = user or AnonymousUser()
    request.session = {}
    return request


class GetModelTestCase(TestCase):
    def test_unknown_model(self):
        for public in [True, False]:
            with self.subTest(public=public):
                self.assertIsNone(get_model("testapp.Missing", public))

    def test_public_allowed_model(self):
        self.assertIs(get_model("wagtailcore.Page", public=True), Page)

    def test_public_model_not_in_allow_list(self):
        self.assertIsNone(get_model("auth.User", public=True))

    def test_admin_ignores_allow_list(self):
        self.assertIs(get_model("auth.User", public=False), User)


class GetPublicRulesTestCase(TestCase):
    def setUp(self):
        self.parent_page = Page.objects.get(depth=1).add_child(
            instance=Page(title="Parent")
        )

    def test_model_not_in_allow_list(self):
        self.assertIsNone(get_public_rules(User))

    @override_settings(
        WAGTAILAUTOCOMPLETE_ALLOW_PUBLIC_MODELS={"testapp.Person": [allow_all]}
    )
    def test_model_entry(self):
        self.assertEqual(get_public_rules(Person), [allow_all])

    @override_settings(WAGTAILAUTOCOMPLETE_ALLOW_PUBLIC_MODELS={"testapp.Person": []})
    def test_empty_entry_denies_model(self):
        self.assertIsNone(get_public_rules(Person))

    @override_settings(WAGTAILAUTOCOMPLETE_ALLOW_PUBLIC_MODELS={"testapp.Missing": []})
    def test_unresolvable_label_raises(self):
        with self.assertRaises(ImproperlyConfigured):
            get_public_rules(Person)

    def test_subclass_inherits_parent_rules(self):
        self.assertEqual(
            get_public_rules(RoutablePageTest),
            WAGTAILAUTOCOMPLETE_ALLOW_PUBLIC_MODELS_DEFAULT["wagtailcore.Page"],
        )

    @override_settings(
        WAGTAILAUTOCOMPLETE_ALLOW_PUBLIC_MODELS={
            "wagtailcore.Page": [live_pages],
            "routablepagetests.RoutablePageTest": [allow_all],
        }
    )
    def test_subclass_entry_overrides_parent(self):
        self.assertEqual(get_public_rules(RoutablePageTest), [allow_all])

    @override_settings(
        WAGTAILAUTOCOMPLETE_ALLOW_PUBLIC_MODELS={
            "wagtailcore.Page": [live_pages],
            "routablepagetests.RoutablePageTest": [],
            "routablepagetests.RoutablePageWithOverriddenIndexRouteTest": [],
        }
    )
    def test_denied_subclasses_excluded(self):
        page = self.parent_page.add_child(instance=Page(title="Page"))
        self.parent_page.add_child(instance=RoutablePageTest(title="Routable"))
        self.parent_page.add_child(
            instance=RoutablePageWithOverriddenIndexRouteTest(title="Overridden")
        )

        queryset = Page.objects.child_of(self.parent_page)
        for rule in get_public_rules(Page):
            queryset = rule(queryset, make_request())
        self.assertEqual(list(queryset), [page])


class ApplyAllowRulesTestCase(TestCase):
    def setUp(self):
        self.parent_page = Page.objects.get(depth=1).add_child(
            instance=Page(title="Parent")
        )
        self.parent_page.add_child(instance=Page(title="Public page"))
        self.parent_page.add_child(instance=Page(title="Draft page", live=False))
        self.parent_page.add_child(instance=RoutablePageTest(title="Routable page"))

        restricted_page = self.parent_page.add_child(
            instance=Page(title="Restricted page")
        )
        PageViewRestriction.objects.create(
            page=restricted_page, restriction_type=PageViewRestriction.LOGIN
        )

    def titles(self, model, public, request=None):
        queryset = apply_allow_rules(
            model.objects.child_of(self.parent_page),
            model,
            request or make_request(),
            public,
        )
        return {page.title for page in queryset}

    def test_public_default_page_rules(self):
        self.assertEqual(
            self.titles(Page, public=True), {"Public page", "Routable page"}
        )

    def test_public_rules_receive_request(self):
        request = make_request(User.objects.create_user("user"))
        self.assertEqual(
            self.titles(Page, public=True, request=request),
            {"Public page", "Restricted page", "Routable page"},
        )

    def test_admin_excludes_draft_pages_only(self):
        self.assertEqual(
            self.titles(Page, public=False),
            {"Public page", "Restricted page", "Routable page"},
        )

    def test_admin_excludes_draft_page_subclasses(self):
        RoutablePageTest.objects.update(live=False)
        self.assertEqual(self.titles(RoutablePageTest, public=False), set())
