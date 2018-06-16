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
            'app_label.Author',
            null=True,
            blank=True,
            on_delete=models.SET_NULL,
        )

The ``AuthorPage`` would traditionally be selected with a
:class:`~wagtail:wagtail.wagtailadmin.edit_handlers.PageChooserPanel`,
like the following.

.. code-block:: python

    panels = [
        PageChooserPanel('author', page_type='app_label.AuthorPage'),
    ]

Instead we can use :py:class:`AutocompletePanel`.

.. code-block:: python

    panels = [
        AutocompletePanel('author', page_type='app_label.AuthorPage'),
    ]

AutocompletePanel
=================

.. module:: wagtailautocomplete.edit_handlers

.. class:: AutocompletePanel(field_name, page_type='wagtailcore.Page', is_single=True)

    ``AutocompletePanel`` takes one required argument, the field name.
    Optionally, you can pass a single ``page_type`` which will limit the
    objects an editor can select to that model — this argument should be
    passed in ``app_label.ModelName`` syntax.

    ``is_single`` determines whether the editor can select one object (with
    the default value of ``True``) or multiple objects (with ``False``). The
    default value is fine for drop-in
    :class:`~wagtail:wagtail.wagtailadmin.edit_handlers.PageChooserPanel`
    replacement.

    .. note::
        ``AutocompletePanel`` does not currently support receiving ``page_type``
        as a list.
        :class:`~wagtail:wagtail.wagtailadmin.edit_handlers.PageChooserPanel`
        does take multiple page types like this.

    .. note::
        ``AutocompletePanel`` does not currently support receiving the
        ``can_choose_root`` argument that
        :class:`~wagtail:wagtail.wagtailadmin.edit_handlers.PageChooserPanel`
        does.
