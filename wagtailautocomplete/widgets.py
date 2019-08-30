import json

from django.forms import Widget
from wagtail.admin.edit_handlers import widget_with_script

from .views import render_page


class Autocomplete(Widget):
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

    def render(self, name, value, attrs=None, renderer=None):
        return widget_with_script(
            super(Autocomplete, self).render(name, value, attrs, renderer),
            self.render_js_init(attrs['id']))

    def render_js_init(self, id):
        return "window.initAutoCompleteWidget('{0}');".format(id)
