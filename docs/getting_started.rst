===============
Getting Started
===============

:doc:`Wagtail Autocomplete <index>` provides an edit handler that allows an editor to
select related objects via a quick autocompleted searching interface.

Requirements
============

Wagtail Autocomplete requires Wagtail version 1.11 or newer.

.. warning::

    We do not currently support Wagtail 2.x, but we're working on it!

Installation
============

Install with ``pip``:

.. code-block:: sh

    pip install https://github.com/emilyhorsman/wagtail-autocomplete/tarball/master/

Setup
=====

Add ``'wagtail-autocomplete'`` to your projects' ``INSTALLED_APPS``. This enables Wagtail to auto-discover the Wagtail Autocomplete's admin hooks.

Add Wagtail Autocomplete's url patterns to your project's url config, usually in ``urls.py``. This should still come before your ``wagtail_urls``:

.. code-block:: python

    from django.conf.urls import include, url

    from wagtail.wagtailcore import urls as wagtail_urls

    from autocomplete.urls.admin import urlpatterns as autocomplete_admin_urls

    urlpatterns = [
        # ...
        url(r'^admin/autocomplete/', include(autocomplete_admin_urls)),
        url(r'', include(wagtail_urls)),
    ]

This makes available custom API endpoints that provide the search and creation behavior for the widget.

Continue to :doc:`Basic Usage <basic_usage>` to learn how to use the ``AutocompletePanel`` on a field in the admin.
