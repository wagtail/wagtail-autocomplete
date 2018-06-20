Wagtail Autocomplete
====================

.. image:: https://circleci.com/gh/wagtail/wagtail-autocomplete.svg?style=svg
    :target: https://circleci.com/gh/wagtail/wagtail-autocomplete

An edit handler for the Wagtail content editor allowing single or multi autocompleted selection of Pages, Snippets, or other models.
The widget is written in React and can be used outside the Wagtail admin, if desired.

Features
~~~~~~~~

* Rapidly select related objects via a smooth autocomplete interface
* A drop-in alternative to ``PageChooserPanel`` or ``SnippetChooserPanel``
* Create new objects from the autocomplete input if your search turns up blank
* React component can be used outside of the Wagtail admin for public-facing forms
* Default theme shares the colour scheme and styles of the Wagtail admin
* Easy to re-theme with `BEM <http://getbem.com/>`_ methodology

Who’s using it?
~~~~~~~~~~~~~~~

* The `U.S. Press Freedom Tracker <https://pressfreedomtracker.us/>`_ makes extensive use of this edit handler with its public-facing filters and content editor to rapidly select and create new related metadata objects.

Merge into wagtail/wagtail
~~~~~~~~~~~~~~~~~~~~~~~~~~

Eventually we would like this to be merged into `wagtail/wagtail <https://github.com/wagtail/wagtail/>`_.
This will require some work on the Wagtail API.

* Support endpoints for non-``Page`` models
* Support standard `Django field lookups <https://docs.djangoproject.com/en/1.11/ref/models/querysets/#id4>`_ such as ``id__in``
* Create objects from the API
* Permission system for non-administrator access to the API

Documentation
~~~~~~~~~~~~~

Our documentation is on `Read the Docs <https://wagtail-autocomplete.readthedocs.io/>`_ and includes `basic usage instructions <https://wagtail-autocomplete.readthedocs.io/en/latest/basic_usage.html>`_ as well as `contribution guidelines <https://wagtail-autocomplete.readthedocs.io/en/latest/contributing.html>`_.

Contributors
~~~~~~~~~~~~

* Harris Lapiroff (Little Weaver Web Collective) for the UX and UI design
* Rachel Stevens (Little Weaver Web Collective)
* Emily Horsman (Little Weaver Web Collective)
