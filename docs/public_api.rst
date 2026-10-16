Public Endpoints
================

Wagtail Autocomplete provides unauthenticated endpoints for use in forms
outside the Wagtail admin.

To enable them, add the public URL patterns to your ``urls.py``:

.. code-block:: python

    from django.urls import include, path
    from wagtailautocomplete.urls import public as autocomplete_public_urls

    urlpatterns = [
        # ...
        path('autocomplete/', include(autocomplete_public_urls)),
    ]

This registers ``GET objects/`` and ``POST search/``, which accept the same
parameters as the admin endpoints.

Allowed models
--------------

The public endpoints only serve models listed in the
``WAGTAILAUTOCOMPLETE_ALLOW_PUBLIC_MODELS`` setting. Requests for any other
model receives a 400 response.

``WAGTAILAUTOCOMPLETE_ALLOW_PUBLIC_MODELS`` maps model labels to a list of
allow rule checkers. Each checker is a callable (or a dotted path to one) that
takes ``(queryset, request)`` and returns the subset of the queryset the
request is allowed to see. Every label must be an installed model, or
``ImproperlyConfigured`` is raised. The default is:

.. code-block:: python

    WAGTAILAUTOCOMPLETE_ALLOW_PUBLIC_MODELS = {
        'wagtailcore.Page': [
            'wagtailautocomplete.allowed.live_pages',
            'wagtailautocomplete.allowed.viewable_pages',
        ],
        'wagtaildocs.Document': ['wagtailautocomplete.allowed.viewable_documents'],
    }

Built-in allow rule callables are:

``live_pages``
    Excludes draft pages. The admin endpoints always apply this to pages.

``viewable_pages``
    Excludes pages under a view restriction (login, password or group) that the
    current request does not satisfy.

``viewable_documents``
    Excludes documents in collections under a view restriction that the current
    request does not satisfy.

An entry also covers subclasses of the model, so allowing
``wagtailcore.Page`` allows every page type, each limited by
``live_pages`` and ``viewable_pages``. If a subclass has its own entry,
that entry's rules are used instead of its parent's.

Each subclass is searched on its own ``autocomplete_search_field``. Ensure
that a parent class does not expose unwanted fields on subclasses, and give
subclasses stricter rules, or deny it, if necessary.

To expose your own models, override the setting. Include the defaults to keep
Wagtail pages and documents available:

.. code-block:: python

    def published_only(queryset, request):
        return queryset.filter(is_published=True)

    def all_authors(queryset, request):
        return queryset

    WAGTAILAUTOCOMPLETE_ALLOW_PUBLIC_MODELS = {
        'wagtailcore.Page': [
            'wagtailautocomplete.allowed.live_pages',
            'wagtailautocomplete.allowed.viewable_pages',
        ],
        # Allow custom autocomplete allow rules for these models
        'myapp.Author': [all_authors],
        'myapp.Book': [published_only],
        # Do not autocomplete StaffPage at all
        'myapp.StaffPage': [],
    }

All models are denied by default, but nn empty list explicitly denies a model.
This is useful for models that are subclasses of a class that is allowed, for
example, you want to deny a specific subclass of Wagtail's ``Page`` model, but
allow others using the default rules.
