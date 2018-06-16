Wagtail Autocomplete
====================

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
--------------------------

Eventually we would like this to be merged into `wagtail/wagtail <https://github.com/wagtail/wagtail/>`_.
This will require some work on the Wagtail API.

* Support endpoints for non-``Page`` models
* Support standard `Django field lookups <https://docs.djangoproject.com/en/1.11/ref/models/querysets/#id4>`_ such as ``id__in``
* Create objects from the API
* Permission system for non-administrator access to the API


Development
~~~~~~~~~~~

Code Style
----------

This repo follows `Wagtail’s guidelines <http://docs.wagtail.io/en/v1.11.1/contributing/index.html>`_.
Clone ``wagtail/wagtail`` in a separate folder and run linters with their configuration.

.. code-block:: sh

    gem install scss_lint
    npm run lint:css -- --config /path/to/wagtail/.scss-lint.yml
    npm run lint:js -- --config /path/to/wagtail/.eslintrc

    flake8 --config /path/to/wagtail/tox.ini wagtailautocomplete
    isort --check-only --diff --recursive wagtailautocomplete

Compiling the documentation
---------------------------

The Wagtail Autocomplete documentation is built with Sphinx. To install Sphinx and compile the documentation, run:

.. code-block:: sh

    cd /path/to/wagtail-autocomplete
    pip install -e .[docs]
    cd docs
    make html

    .. code-block:: console

        $ cd docs/_build/html/
        $ python -m http.server 8080

    Now you can open <http://localhost:8080/> in your web browser to see the compiled documentation.

Contributors
~~~~~~~~~~~~

* Harris Lapiroff (Little Weaver Web Collective) for the UX and UI design
* Rachel Stevens (Little Weaver Web Collective)
* Emily Horsman (Little Weaver Web Collective)
