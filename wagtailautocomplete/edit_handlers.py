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
        def __init__(self, field_name, **kwargs):
            self.field_name = field_name

        def bind_to_model(self, model):
            target_model = model._meta.get_field(self.field_name).remote_field.model
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
        def __init__(self, field_name, **kwargs):
            super().__init__(field_name)

        @property
        def is_single(self):
            # Should cover all manny-to-many relationships
            return not issubclass(self.model._meta.get_field(self.field_name).__class__,
                                  ManyToManyField)

        @property
        def target_model(self):
            return self.model._meta.get_field(self.field_name).remote_field.model

        def on_model_bound(self):
            can_create = _can_create(self.target_model)
            self.widget = type(
                '_Autocomplete',
                (Autocomplete,),
                dict(target_model=self.target_model, can_create=can_create, is_single=self.is_single),
            )
