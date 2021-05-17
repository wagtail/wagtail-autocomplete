from django.core.exceptions import ImproperlyConfigured
from django.db.models import ManyToManyField
from django.utils.functional import cached_property

from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.utils import resolve_model_string

from .widgets import Autocomplete


def _can_create(model):
    """
    Returns True if the given model has implemented the autocomplete_create
    method to allow new instances to be creates from a single string value.
    """
    return callable(getattr(model, 'autocomplete_create', None))


def _is_single_value(db_field):
    """
    Returns True if the given model field accepts a single value only.
    """
    # should cover all many-to-many relationships
    return not isinstance(db_field, ManyToManyField)


class AutocompletePanel(FieldPanel):
    def __init__(self, field_name, target_model=None, **kwargs):
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
                is_single=_is_single_value(self.db_field),
            )
        }

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
