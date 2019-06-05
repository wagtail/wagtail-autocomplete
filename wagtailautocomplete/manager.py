import warnings
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from django.query import QuerySet
    from django.db.models import Model


class AutocompleteManager:
    search_field = 'title'
    label_field = 'title'

    def queryset(self, model_class: type):
        queryset = model_class.objects.all()

        # If this appears to be a Page queryset, filter to live Pages
        if getattr(queryset, 'live', None):
            queryset = queryset.live()

        return queryset

    def search(
        self,
        model_class: type,
        value: Optional[str] = None
    ) -> 'QuerySet':
        query_kwargs = {}

        if value:
            key = '{}__icontains'.format(self.search_field)
            query_kwargs[key] = value

        queryset = self.queryset(model_class).filter(**query_kwargs)

        return queryset

    def label(self, obj: 'Model') -> str:
        return getattr(obj, self.label_field)


default_manager = AutocompleteManager()


def get_manager_for_model(model: type):
    if hasattr(model, 'autocomplete_manager'):
        manager = model.autocomplete_manager
    elif any(
        hasattr(model, 'autocomplete_search_field'),
        hasattr(model, 'autocomplete_create'),
        hasattr(model, 'autocomplete_label'),
    ):
        # This entire elif block can be removed when the on-model methods and
        # attributes are retired and undocumented
        warnings.warn(
            'The autocomplete_search_field, autocomplete_create, and '
            'autocomplete_label properties are deprecated and will be '
            'removed. Use a custom AutocompleteManager instead.',
            DeprecationWarning
        )

        class TemporaryManager(AutocompleteManager):
            # This is a value
            search_field = getattr(
                model,
                'autocomplete_search_field',
                default_manager.search_field
            )
            # This is a method
            label = getattr(
                model,
                'autocomplete_label',
                default_manager.label
            )
            create = getattr(
                model,
                'autocomplete_create',
                None
            )

        manager = TemporaryManager()
    else:
        manager = default_manager

    return manager
