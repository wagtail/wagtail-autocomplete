import warnings

from django.apps import apps
from wagtail import VERSION

from .widgets import Autocomplete


def _can_create(model_string):
    """Returns True if the given model has implemented the autocomplete_create
    method to allow new instances to be creates from a single string value.
    """
    return callable(getattr(
        apps.get_model(model_string),
        'autocomplete_create',
        None,
    ))


if VERSION < (2, 0):
    # Wagtail 1.x
    from wagtail.wagtailadmin.edit_handlers import BaseFieldPanel

    class AutocompletePanel:
        def __init__(self, field_name, target_model='wagtailcore.Page', is_single=True, **kwargs):
            # is_single defaults to True in order to have easy drop-in
            # compatibility with wagtailadmin.edit_handlers.PageChooserPanel.
            self.field_name = field_name
            self.target_model = target_model
            self.is_single = is_single
            # For compatability with old 'page_type' argument
            if 'page_type' in kwargs:
                warnings.warn(
                    'page_type argument has been replaced with target_model',
                    DeprecationWarning
                )
                self.target_model = kwargs['page_type']

        def bind_to_model(self, model):
            can_create = _can_create(self.target_model)
            base = dict(
                model=model,
                field_name=self.field_name,
                widget=type(
                    '_Autocomplete',
                    (Autocomplete,),
                    dict(target_model=self.target_model, can_create=can_create, is_single=self.is_single),
                ),
            )
            return type('_AutocompleteFieldPanel', (BaseFieldPanel,), base)
else:
    # Wagtail 2.x
    from wagtail.admin.edit_handlers import FieldPanel

    class AutocompletePanel(FieldPanel):
        def __init__(self, field_name, target_model='wagtailcore.Page', is_single=True, **kwargs):
            # is_single defaults to True in order to have easy drop-in
            # compatibility with wagtailadmin.edit_handlers.PageChooserPanel.
            self.target_model = target_model
            self.is_single = is_single
            # For compatability with old 'page_type' argument
            if 'page_type' in kwargs:
                warnings.warn(
                    'page_type argument has been replaced with target_model',
                    DeprecationWarning
                )
                self.target_model = kwargs['page_type']
                del kwargs['page_type']
            super().__init__(field_name, **kwargs)

        def clone(self):
            return self.__class__(
                field_name=self.field_name,
                target_model=self.target_model,
                is_single=self.is_single
            )

        def on_model_bound(self):
            can_create = _can_create(self.target_model)
            self.widget = type(
                '_Autocomplete',
                (Autocomplete,),
                dict(target_model=self.target_model, can_create=can_create, is_single=self.is_single),
            )
