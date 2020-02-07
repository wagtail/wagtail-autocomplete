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

    Additionally, this means that ``autocomplete_search_field`` *must* be a model field and cannot be an arbitrary property or method.

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
