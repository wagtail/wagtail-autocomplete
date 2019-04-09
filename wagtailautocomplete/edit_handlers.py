import warnings

from django.apps import apps
from django.db.models import ManyToManyField
from wagtail import VERSION

from .widgets import Autocomplete


def _can_create(model):
    """Returns True if the given model has implemented the autocomplete_create
    method to allow new instances to be creates from a single string value.
    """
    return callable(getattr(
        model,
        'autocomplete_create',
        None,
    ))


if VERSION < (2, 0):
    # Wagtail 1.x
    from wagtail.wagtailadmin.edit_handlers import BaseFieldPanel

    class AutocompletePanel:
        def __init__(self, field_name, target_model=None, **kwargs):
            self.field_name = field_name
            self.target_model = target_model
            # For compatability with old 'page_type' argument
            if 'page_type' in kwargs:
                warnings.warn(
                    'page_type argument has been replaced with target_model',
                    DeprecationWarning
                )
                self.target_model = kwargs['page_type']

        def bind_to_model(self, model):
            if not self.target_model:
                target_model = model._meta.get_field(self.field_name).remote_field.model
            elif isinstance(self.target_model, str):
                target_model = apps.get_model(self.target_model)
            else:
                target_model = self.target_model

            is_single = not issubclass(model._meta.get_field(self.field_name).__class__,
                                       ManyToManyField)
            can_create = _can_create(target_model)

            base = dict(
                model=model,
                field_name=self.field_name,
                widget=type(
                    '_Autocomplete',
                    (Autocomplete,),
                    dict(target_model=target_model, can_create=can_create, is_single=is_single),
                ),
            )
            return type('_AutocompleteFieldPanel', (BaseFieldPanel,), base)
else:
    # Wagtail 2.x
    from wagtail.admin.edit_handlers import FieldPanel

    class AutocompletePanel(FieldPanel):
        def __init__(self, field_name, target_model=None, **kwargs):
            # For compatability with old 'page_type' argument
            if 'page_type' in kwargs:
                warnings.warn(
                    'page_type argument has been replaced with target_model',
                    DeprecationWarning
                )
                target_model = kwargs['page_type']
                del kwargs['page_type']
            self.target_model = target_model
            super().__init__(field_name, **kwargs)

        def clone(self):
            return self.__class__(
                field_name=self.field_name,
                target_model=self.target_model,
            )

        @property
        def is_single(self):
            # Should cover all manny-to-many relationships
            return not issubclass(self.model._meta.get_field(self.field_name).__class__,
                                  ManyToManyField)

        def resolve_target_model(self):
            if not self.target_model:
                return self.model._meta.get_field(self.field_name).remote_field.model
            elif isinstance(self.target_model, str):
                return apps.get_model(self.target_model)
            return self.target_model

        def on_model_bound(self):
            target_model = self.resolve_target_model()
            can_create = _can_create(target_model)
            self.widget = type(
                '_Autocomplete',
                (Autocomplete,),
                dict(target_model=target_model, can_create=can_create, is_single=self.is_single),
            )
