==================
Using Other Models
==================

:class:`AutocompletePanel` works with models other than
:class:`~wagtail:wagtail.wagtailcore.Page` and subclasses of it.


Selecting Snippets
==================

For example, we have a Django model ``Link`` that we have registered as a snippet.
We also have a ``BlogPage`` model that would traditionally use a
:class:`~wagtail:wagtail.wagtailsnippets.edit_handlers.SnippetChooserPanel`


.. code-block:: python

    from django.db import models

    from wagtail.wagtailadmin.edit_handlers import FieldPanel
    from wagtail.wagtailcore.models import Page
    from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
    from wagtail.wagtailsnippets.models import register_snippet

    @register_snippet
    class Link(models.Model):
        title = models.CharField(max_length=255)
        url = models.URLField()

        panels = [
            FieldPanel('title'),
            FieldPanel('url'),
        ]


    class BlogPage(Page):
        external_link = models.ForeignKey(
            'app_label.Link',
            null=True,
            blank=True,
            on_delete=models.SET_NULL,
        )

        content_panels = [
            SnippetChooserPanel('external_link'),
        ]

We can replace the
:class:`~wagtail:wagtail.wagtailsnippets.edit_handlers.SnippetChooserPanel`
usage with
:class:`AutocompletePanel`.

.. code-block:: python

    panels = [
        AutocompletePanel('external_link'),
    ]

.. note::
    Wagtail Autocomplete assumes by default that models have a ``title`` field.
    To you autocomplete with target models that don't have a ``title`` field,
    see :doc:`Customization <customization>` for instructions on setting a
    custom label and search field.
