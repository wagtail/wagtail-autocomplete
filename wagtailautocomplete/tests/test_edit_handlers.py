from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured
from django.test import RequestFactory, TestCase
from wagtail import VERSION as WAGTAIL_VERSION

if WAGTAIL_VERSION >= (3, 0):
    from wagtail.admin.panels import ObjectList
else:
    from wagtail.admin.edit_handlers import ObjectList

from bs4 import BeautifulSoup

from wagtailautocomplete.edit_handlers import AutocompletePanel
from wagtailautocomplete.widgets import Autocomplete

from .testapp.models import House, Person


class TestAutocompletePanel(TestCase):
    def setUp(self):
        self.request = RequestFactory().get('/')
        user = AnonymousUser()
        self.request.user = user

        model = House  # a model with a foreign key to Person

        # a AutocompletePanel class that works on House's 'owner' field
        if WAGTAIL_VERSION >= (3, 0):
            self.edit_handler = ObjectList([AutocompletePanel("owner")]).bind_to_model(House)
        else:
            self.edit_handler = ObjectList([AutocompletePanel("owner")]).bind_to(
                model=House, request=self.request
            )

        self.base_autocomplete_panel = self.edit_handler.children[0]

        # build a form class containing the fields that AutocompletePanel wants
        self.form_class = self.edit_handler.get_form_class()

        # a test instance of House with an owner and an occupant
        self.house_owner = Person.objects.create(name="An owner")
        self.house_occupant = Person.objects.create(name="An occupant")
        self.test_house = model.objects.create(
            owner=self.house_owner, occupants=[self.house_occupant]
        )

        self.form = self.form_class(instance=self.test_house)

        if WAGTAIL_VERSION >= (3, 0):
            self.autocomplete_panel = self.base_autocomplete_panel.get_bound_panel(
                instance=self.test_house, form=self.form
            )
        else:
            self.autocomplete_panel = self.base_autocomplete_panel.bind_to(
                instance=self.test_house, form=self.form
            )

    def test_form_field_uses_correct_widget(self):
        self.assertEqual(type(self.form.fields['owner'].widget), Autocomplete)

    def test_form_field_media(self):
        media_html = str(self.form.media)

        self.assertIn('wagtailautocomplete/dist.css', media_html)
        self.assertIn('wagtailautocomplete/dist.js', media_html)

    def test_render_js_init(self):
        result = self.autocomplete_panel.render_as_field()

        self.assertIn('initAutoCompleteWidget("id_owner");', result)

    def test_render_as_field(self):
        result = self.autocomplete_panel.render_as_field()
        self.assertIn('<p class="help">the owner</p>', result)

        soup = BeautifulSoup(result, 'html5lib')
        elements = soup.find_all(attrs={'data-autocomplete-input': True})

        self.assertEqual(len(elements), 1)
        self.assertEqual(elements[0]['data-autocomplete-input-name'], 'owner')
        self.assertJSONEqual(elements[0]['data-autocomplete-input-value'], {
            'pk': self.house_owner.pk,
            'title': self.house_owner.name,
        })
        self.assertNotIn('data-autocomplete-input-can-create', elements[0].attrs)
        self.assertIn('data-autocomplete-input-is-single', elements[0].attrs)

        # test the conversion of the form field's value from datadict
        field_value = elements[0]['data-autocomplete-input-value']
        form = self.form_class({'owner': field_value}, instance=self.test_house)

        self.assertTrue(form.is_valid())

    def test_render_as_empty_field(self):
        test_instance = House()
        form = self.form_class(instance=test_instance)
        if WAGTAIL_VERSION >= (3, 0):
            autocomplete_panel = self.base_autocomplete_panel.get_bound_panel(
                instance=test_instance, form=form, request=self.request
            )
        else:
            autocomplete_panel = self.base_autocomplete_panel.bind_to(
                instance=test_instance, form=form, request=self.request
            )
        result = autocomplete_panel.render_as_field()

        self.assertIn('<p class="help">the owner</p>', result)

        soup = BeautifulSoup(result, 'html5lib')
        element = soup.find(attrs={'data-autocomplete-input': True})

        self.assertIsNotNone(element)
        self.assertEqual(element['data-autocomplete-input-name'], 'owner')
        self.assertEqual(element['data-autocomplete-input-value'], 'null')
        self.assertNotIn('data-autocomplete-input-can-create', element.attrs)
        self.assertIn('data-autocomplete-input-is-single', element.attrs)

    def test_render_multiple_as_field(self):
        if WAGTAIL_VERSION >= (3, 0):
            edit_handler = ObjectList([AutocompletePanel('occupants')]).bind_to_model(House)
        else:
            edit_handler = ObjectList([AutocompletePanel('occupants')]).bind_to(
                model=House, request=self.request
            )

        form_class = edit_handler.get_form_class()
        form = form_class(instance=self.test_house)

        if WAGTAIL_VERSION >= (3, 0):
            autocomplete_panel = edit_handler.children[0].get_bound_panel(
                instance=self.test_house, form=form, request=self.request
            )
        else:
            autocomplete_panel = edit_handler.children[0].bind_to(
                instance=self.test_house, form=form, request=self.request
            )

        result = autocomplete_panel.render_as_field()
        self.assertIn('Occupants', result)

        soup = BeautifulSoup(result, 'html5lib')
        element = soup.find(attrs={'data-autocomplete-input': True})

        self.assertIsNotNone(element)
        self.assertEqual(element['data-autocomplete-input-name'], 'occupants')
        self.assertJSONEqual(element['data-autocomplete-input-value'], [
            {
                'pk': self.house_occupant.pk,
                'title': self.house_occupant.name,
            }
        ])
        self.assertNotIn('data-autocomplete-input-can-create', element.attrs)
        self.assertNotIn('data-autocomplete-input-is-single', element.attrs)

        # test the conversion of the form field's value from datadict
        field_value = element['data-autocomplete-input-value']
        form = form_class({'occupants': field_value}, instance=self.test_house)

        self.assertTrue(form.is_valid())

    def test_render_create_as_field(self):
        if WAGTAIL_VERSION >= (3, 0):
            edit_handler = ObjectList([AutocompletePanel('group')]).bind_to_model(Person)
        else:
            edit_handler = ObjectList([AutocompletePanel('group')]).bind_to(
                model=Person, request=self.request
            )

        form_class = edit_handler.get_form_class()
        form = form_class(instance=self.house_occupant)

        if WAGTAIL_VERSION >= (3, 0):
            autocomplete_panel = edit_handler.children[0].get_bound_panel(
                instance=self.house_occupant, form=form, request=self.request
            )
        else:
            autocomplete_panel = edit_handler.children[0].bind_to(
                instance=self.house_occupant, form=form, request=self.request
            )

        result = autocomplete_panel.render_as_field()
        self.assertIn('Group', result)

        soup = BeautifulSoup(result, 'html5lib')
        element = soup.find(attrs={'data-autocomplete-input': True})

        self.assertIsNotNone(element)
        self.assertEqual(element['data-autocomplete-input-name'], 'group')
        self.assertJSONEqual(element['data-autocomplete-input-value'], 'null')
        self.assertIn('data-autocomplete-input-can-create', element.attrs)
        self.assertIn('data-autocomplete-input-is-single', element.attrs)

    def test_render_error(self):
        form = self.form_class({'owner': ''}, instance=self.test_house)
        self.assertFalse(form.is_valid())

        form = self.form_class({'owner': 'null'}, instance=self.test_house)
        self.assertFalse(form.is_valid())

        if WAGTAIL_VERSION >= (3, 0):
            autocomplete_panel = self.base_autocomplete_panel.get_bound_panel(
                instance=self.test_house, form=form, request=self.request
            )
        else:
            autocomplete_panel = self.base_autocomplete_panel.bind_to(
                instance=self.test_house, form=form, request=self.request
            )

        self.assertIn('<span>This field is required.</span>', autocomplete_panel.render_as_field())

    def test_target_model(self):
        if WAGTAIL_VERSION >= (3, 0):
            autocomplete_panel = AutocompletePanel('owner', target_model=Person).bind_to_model(House)
        else:
            autocomplete_panel = AutocompletePanel('owner', target_model=Person).bind_to(model=House)

        self.assertEqual(autocomplete_panel.target_model, Person)

    def test_target_models_malformed_type(self):
        if WAGTAIL_VERSION >= (3, 0):
            autocomplete_panel = AutocompletePanel('owner', target_model='testapp').bind_to_model(House)
        else:
            autocomplete_panel = AutocompletePanel('owner', target_model='testapp').bind_to(model=House)

        with self.assertRaises(ImproperlyConfigured):
            autocomplete_panel.target_model

    def test_target_models_nonexistent_type(self):
        if WAGTAIL_VERSION >= (3, 0):
            autocomplete_panel = AutocompletePanel('owner', target_model='testapp.hous').bind_to_model(House)
        else:
            autocomplete_panel = AutocompletePanel('owner', target_model='testapp.hous').bind_to(model=House)

        with self.assertRaises(ImproperlyConfigured):
            autocomplete_panel.target_model
