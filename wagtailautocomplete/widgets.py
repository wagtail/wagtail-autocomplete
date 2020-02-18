import json

from django import forms

from wagtail.admin.staticfiles import versioned_static
from wagtail.utils.widgets import WidgetWithScript

from .views import render_page


class Autocomplete(WidgetWithScript):
    template_name = 'wagtailautocomplete/autocomplete.html'

    def get_context(self, *args, **kwargs):
        context = super(Autocomplete, self).get_context(*args, **kwargs)
        context['widget']['target_model'] = self.target_model._meta.label
        context['widget']['can_create'] = self.can_create
        context['widget']['is_single'] = self.is_single
        return context

    def format_value(self, value):
        if not value:
            return 'null'
        if type(value) == list:
            return json.dumps([
                render_page(page)
                for page in self.target_model.objects.filter(pk__in=value)
            ])
        else:
            return json.dumps(render_page(self.target_model.objects.get(pk=value)))

    def value_from_datadict(self, data, files, name):
        value = json.loads(data.get(name))
        if not value:
            return None

        if type(value) == list:
            return [obj['pk'] for obj in value]

        return value['pk']

    def render_js_init(self, id_, name, value):
        return "initAutoCompleteWidget({id});".format(
            id=json.dumps(id_),
        )

    @property
    def media(self):
        return forms.Media(
            css={
                'all': [versioned_static('wagtailautocomplete/dist.css')],
            },
            js=[versioned_static('wagtailautocomplete/dist.js')],
        )
