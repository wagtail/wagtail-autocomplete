===========
Basic Usage
===========

A Quick Example
===============

We have a ``BlogPage`` that lets the editor select an ``AuthorPage`` page.

.. code-block:: python

    class AuthorPage(Page):
        pass

    class BlogPage(Page):
        author = models.ForeignKey(
            'app_label.AuthorPage',
            null=True,
            blank=True,
            on_delete=models.SET_NULL,
        )

The ``AuthorPage`` would traditionally be selected with a
:class:`~wagtail:wagtail.wagtailadmin.edit_handlers.PageChooserPanel`,
like the following.

.. code-block:: python

    content_panels = Page.content_panels + [
        PageChooserPanel('author', page_type='app_label.AuthorPage'),
    ]

Instead we can use :py:class:`AutocompletePanel`.

.. code-block:: python

    content_panels = Page.content_panels + [
        AutocompletePanel('author', target_model='app_label.AuthorPage'),
    ]

.. image:: /_static/autocomplete-fk-demo.gif
    :alt: Animation of autocomplete selection in action

AutocompletePanel
=================

.. module:: wagtailautocomplete.edit_handlers

.. class:: AutocompletePanel(field_name, target_model='wagtailcore.Page', is_single=True)

    ``AutocompletePanel`` takes one required argument, the field name.
    Optionally, you can pass a single ``target_model`` which will limit the
    objects an editor can select to that model — this argument should be
    passed in ``app_label.ModelName`` syntax.

    ``is_single`` determines whether the editor can select one object (with
    the default value of ``True``) or multiple objects (with ``False``). The
    default value is fine for drop-in
    :class:`~wagtail:wagtail.wagtailadmin.edit_handlers.PageChooserPanel`
    replacement.

    .. note::
        Unlike :class:`~wagtail:wagtail.wagtailadmin.edit_handlers.PageChooserPanel`,
        ``AutocompletePanel`` does not support receiving ``target_model`` as a list.

    .. note::
        ``AutocompletePanel`` does not support receiving the ``can_choose_root``
        argument that :class:`~wagtail:wagtail.wagtailadmin.edit_handlers.PageChooserPanel`
        does.

Multiple Selection With Clusterable Models
==========================================

``AutocompletePanel`` can also be used with a ``ParentalManyToManyField`` to
provide a multiple selection widget. You must pass ``is_single=False``
explicitly to enable this behavior. For example:

.. code-block:: python

    from django.db import models
    from wagtail.core.models import Page
    from modelcluster.models import ClusterableModel
    from modelcluster.fields import ParentalManyToManyField

    from wagtailautocomplete.edit_handlers import AutocompletePanel

    class Book(ClusterableModel):
        title = models.CharField(max_length=255)


    class AuthorPage(Page):
        books = ParentalManyToManyField(
            Book,
            null=True,
            related_name='authors'
        )

        content_panels = Page.content_panels + [
            AutocompletePanel('books', target_model='home.Book', is_single=False)
        ]

.. image:: /_static/autocomplete-m2m-demo.gif
    :alt: Animation of autocomplete multiple selection in action

.. note::
    This above screen capture also shows the availability of Wagtail
    Autocomplete's "Create New" behavior. To learn more, see
    :doc:`Customization <customization>`.
