===============
Getting Started
===============

Installation
============

Install with ``pip``:

.. code-block:: sh

    pip install wagtail-autocomplete

Setup
=====

Add ``'wagtailautocomplete'`` to your project's ``INSTALLED_APPS``.

Add Wagtail Autocomplete's URL patterns to your project's URL config, usually in ``urls.py``. This should come before your ``wagtail_urls`` and if you are using the suggested pattern ``r'^admin/autocomplete/'`` it must also come before your admin urls:

.. code-block:: python

    from django.conf.urls import include, url

    from wagtail import urls as wagtail_urls

    from wagtailautocomplete.urls.admin import urlpatterns as autocomplete_admin_urls

    urlpatterns = [
        # ...
        path('admin/autocomplete/', include(autocomplete_admin_urls)),
        path("admin/", include(wagtailadmin_urls)),
        # ...
        path("", include(wagtail_urls)),
    ]

This makes available custom API endpoints that provide the search and creation behavior for the widget.

Continue to :doc:`Basic Usage <basic_usage>` to learn how to use the ``AutocompletePanel`` on a field in the admin.
