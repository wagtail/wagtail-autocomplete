import warnings

from django.apps import apps
from django.db.models import ManyToManyField
from wagtail.admin.edit_handlers import FieldPanel

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


class AutocompletePanel(FieldPanel):
    def __init__(self, field_name, target_model=None, **kwargs):
        # For compatability with old 'page_type' argument
        if 'page_type' in kwargs:
            warnings.warn(
                'page_type argument has been replaced with target_model',
                DeprecationWarning
            )
            target_model = kwargs.pop('page_type', None)
        if 'is_single' in kwargs:
            warnings.warn('is_single argument is no longer used', DeprecationWarning)
        self.target_model_kwarg = target_model

        kwargs.pop('is_single', None)  # Deprecated kwarg
        super().__init__(field_name, **kwargs)

    def clone(self):
        return self.__class__(
            field_name=self.field_name,
            target_model=self.target_model_kwarg,
        )

    @property
    def is_single(self):
        # Should cover all many-to-many relationships
        return not issubclass(self.model._meta.get_field(self.field_name).__class__,
                              ManyToManyField)

    @property
    def target_model(self):
        if not self.target_model_kwarg:
            return self.model._meta.get_field(self.field_name).remote_field.model
        elif isinstance(self.target_model_kwarg, str):
            return apps.get_model(self.target_model_kwarg)
        return self.target_model_kwarg

    def on_model_bound(self):
        target_model = self.target_model
        can_create = _can_create(target_model)
        self.widget = type(
            '_Autocomplete',
            (Autocomplete,),
            dict(target_model=target_model, can_create=can_create, is_single=self.is_single),
        )
