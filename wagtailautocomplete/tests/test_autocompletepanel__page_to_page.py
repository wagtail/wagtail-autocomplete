from bs4 import BeautifulSoup

from django.test import TestCase
from django.contrib.auth import get_user_model

from wagtail.core.models import Site

from .testapp.models.page_to_page import SingleAutocompletePage


User = get_user_model()


class PageToPageTestCase(TestCase):
    def setUp(self):
        self.site = Site.objects.get()
        self.root_page = self.site.root_page
        self.superuser = User.objects.create(
            username='testuser',
            password='unusable',
            is_superuser=True,
        )

    def test_autocomplete_widget_renders(self):
        """
        There should be exactly one autocomplete input on the create page for
        a new SingleAutocompletePage
        """

        self.client.force_login(self.superuser)
        create_page_url = '/admin/pages/add/{app_label}/{model_name}/{root_pk}/'.format(
            app_label=SingleAutocompletePage._meta.app_label,
            model_name=SingleAutocompletePage._meta.model_name,
            root_pk=self.site.root_page.pk,
        )
        response = self.client.get(create_page_url)
        # Drill down through the html looking for a properly rendered
        # Autocomplete Panel
        soup = BeautifulSoup(response.content, 'html5lib')
        autocomplete_inputs = soup.select('[data-autocomplete-input]')
        self.assertEqual(len(autocomplete_inputs), 1)
