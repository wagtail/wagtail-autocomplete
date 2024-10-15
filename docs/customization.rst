=============
Customization
=============

Wagtail Autocomplete provides the ability to customize the behavior of ``AutocompletePanel``.

"Create New" Behavior
=====================

Sometimes you want users to not only be able to select pages or objects, but create new ones on the fly without leaving the object that they're currently editing. This can be particularly useful for tag-like objects, where you want to be able to add a tag with a particular title, even if that tag doesn't already exist in the database.

You can enable this type of behavior by defining an ``autocomplete_create`` class method on your model. This method should accept a string value and return a new saved model instance:

.. code-block:: python

    from django.db import models
    from wagtailautocomplete.edit_handlers import AutocompletePanel


    class MyModel(models.Model):
        title = models.CharField(max_length=255)

        @classmethod
        def autocomplete_create(kls: type, value: str):
            return kls.objects.create(title=value)

Custom Search Field
===================

With A Model Method
-------------------

By default, the autocomplete widget will match input against the ``title`` field on your model. If you're using a model that doesn't have a ``title`` attribute, or you just want to search using a different field, you can customize which field it matches against by defining an ``autocomplete_search_field`` property on your model:

.. code-block:: python

    from django.db import models
    from wagtailautocomplete.edit_handlers import AutocompletePanel


    class MyModel(models.Model):
        my_special_field = models.CharField(max_length=255)

        autocomplete_search_field = 'my_special_field'

.. warning::
    You will also need to define an ``autocomplete_label`` function, unless your model has a ``title`` attribute. See the section on Custom Label Display for more information.

.. note::

    Internally Wagtail Autocomplete uses an ``icontains`` lookup to search for partial text matches. So, in the example above, if a user enters ``'part'`` into an autocomplete field, Wagtail Autocomplete will perform the following query to find matches:

    .. code-block:: python

        MyModel.objects.filter(my_special_field__icontains='part')

    Additionally, this means that ``autocomplete_search_field`` *must* be a model field and cannot be an arbitrary property or method. There is also the possibility to define a custom filter function, described in `Custom QuerySet Filter Function`_.

With A Setting
--------------

Alternatively, you may define the search field in a ``WAGTAILAUTOCOMPLETE_CUSTOM_SEARCH_FIELD`` setting:


.. code-block:: python

    # settings.py file
    ...
    WAGTAILAUTOCOMPLETE_CUSTOM_SEARCH_FIELD = {
        "myapp.MyModel": "name",
    }

Or the search field may be a callable:

.. code-block:: python

    # settings.py file
    ...
    WAGTAILAUTOCOMPLETE_CUSTOM_SEARCH_FIELD = {
        "myapp.MyModel": lambda my_model: f"{my_model.first_name} {my_model.last_name}",
    }

.. note::

    If you define both an ``autocomplete_search_field`` method on your model and an entry for your model in the ``WAGTAILAUTOCOMPLETE_CUSTOM_SEARCH_FIELD`` setting, the method on your model will take precedence.


Custom Label Display
====================

By default, the autocomplete widget will display the ``title`` field from a model. You can change this behavior by defining an ``autocomplete_label`` method on your model:

.. code-block:: python

    from django.db import models
    from wagtailautocomplete.edit_handlers import AutocompletePanel


    class MyModel(models.Model):
        my_special_field = models.CharField(max_length=255)

        def autocomplete_label(self):
            return self.my_special_field

.. _Custom QuerySet Filter Function:

Custom QuerySet Filter Function
====================

With A Model Method
-------------------

By default, the autocomplete widget uses an ``icontains`` lookup to search for matching items of the given model. To change that behavior a custom filter function can be defined, that will be called instead of the default filtering. The function needs to return a QuerySet of the expected model.

.. code-block:: python

    from django.db import models
    from django.db.models import QuerySet
    from wagtailautocomplete.edit_handlers import AutocompletePanel


    class MyModel(models.Model):
        my_special_field = models.CharField(max_length=255)

        def autocomplete_label(self):
            return self.my_special_field
        
        @staticmethod
        def autocomplete_custom_queryset_filter(search_term: str) -> QuerySet:
            field_name='my_special_field'
            filter_kwargs = dict()
            filter_kwargs[field_name + '__contains'] = search_term
            return MyModel.objects.filter(**filter_kwargs)

With A Setting
--------------

You may also define custom queryset filtering through a ``WAGTAILAUTOCOMPLETE_CUSTOM_FILTER_FIELDS`` setting:

.. code-block:: python

    # settings.py
    ...
    WAGTAILAUTOCOMPLETE_CUSTOM_FILTER_FIELDS = {
        "myapp.MyModel": {"fields": ["first_name", "last_name"]},
    }

By default, the filtering will use an OR relation for the fields. If you prefer a different relation, you may define it by passing in a ``connector`` at the same level as ``fields``:

.. code-block:: python

    # settings.py
    from django.db.models import Q
    ...
    WAGTAILAUTOCOMPLETE_CUSTOM_FILTER_FIELDS = {
        "myapp.MyModel": {"fields": ["first_name", "last_name"], "connector": Q.AND},
    }


.. note::

    If you define both an ``autocomplete_custom_queryset_filter`` method on your model and an entry for your model in the ``WAGTAILAUTOCOMPLETE_CUSTOM_FILTER_FIELDS`` setting, the method on your model will take precedence.
