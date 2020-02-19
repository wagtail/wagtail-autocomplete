import warnings

from django.core.exceptions import ImproperlyConfigured
from django.db.models import ManyToManyField
from django.utils.functional import cached_property

from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.utils import resolve_model_string

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
            del kwargs['is_single']

        super().__init__(field_name, **kwargs)

        self._target_model = target_model

    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs['target_model'] = self._target_model
        return kwargs

    def widget_overrides(self):
        return {
            self.field_name: Autocomplete(
                target_model=self.target_model,
                can_create=_can_create(self.target_model),
                is_single=self.is_single,
            )
        }

    @cached_property
    def is_single(self):
        # Should cover all many-to-many relationships
        return not issubclass(self.db_field.__class__, ManyToManyField)

    @cached_property
    def target_model(self):
        if self._target_model:
            try:
                return resolve_model_string(self._target_model)
            except LookupError:
                raise ImproperlyConfigured(
                    "{0}.target_model must be of the form 'app_label.model_name', "
                    "given {1!r}".format(
                        self.__class__.__name__, self._target_model
                    )
                )
            except ValueError:
                raise ImproperlyConfigured(
                    "{0}.target_model refers to model {1!r} that has not been installed".format(
                        self.__class__.__name__, self._target_model
                    )
                )
        return self.db_field.remote_field.model
