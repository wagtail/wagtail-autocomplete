=========
Changelog
=========

Unreleased
----------

* Remove tests for Wagtail 4.2 and 5.0 as they have reached their EOL
* Added Wagtail 5.x compatibility
* Added tests for Python 3.10 and 3.11
* Remove support for versions of Wagtail < 4.1 (Wagtail 4.1 or later now required)

0.11 Release
------------

* Add handling of validation errors during creation of objects.
* Fix bug where searches failed if Django's CSRF cookie was configured with ``CSRF_COOKIE_HTTPONLY`` set to ``True``
* Update Javascript dependencies to remove security vulnerabilities.

0.10 Release
------------

* Change the search view to use the HTTP POST method, which can prevent the request URI from becoming too long.
* New feature: add the possibility of a custom filter function.

0.9 Release
-----------

* Add Wagtail 3.x compatibility

0.8.1 Release
-------------

* Change in behavior: the autocomplete endpoint will return a 404 response if no objects are found.
* Update Javascript dependencies to remove security vulnerabilities.

0.7 Release
-----------

* Breaking change: Drop deprecated ``page_type`` and ``is_single`` arguments from ``AutocompletePanel``.
* Update the panel and widget codes based on panels of ``wagtail.admin.edit_handlers`` -- mainly ``PageChooserPanel``.
* Update Javascript dependencies to remove security vulnerabilities.
* Update use of deprecated ``django.conf.urls.url`` function.

0.6.3 Release
-------------

* Remove native browser autocomplete form field.

0.6 Release
-----------

* Add Wagtail 2.8 support

0.5 Release
-----------

* Add Django 3.0 support
* Remove Wagtail 1.x support (Wagtail 2.3 or later now required)
* Documentation fixes

0.4 Release
-----------

* Deprecate ``is_single`` option, make ``target_model`` optional. ``AutocompletePanel`` will now automatically derive these attributes from the field. (`#48 <https://github.com/wagtail/wagtail-autocomplete/pull/48>`_)
* Remove compatibility for all Python 2.x and Wagtail 1.x versions (`#53 <https://github.com/wagtail/wagtail-autocomplete/pull/53>`_)

0.3.1 Release
-------------

* Correct documentation for installing tests (`#44 <https://github.com/wagtail/wagtail-autocomplete/pull/44>`_)
* Correct errors raised by endpoints (`#45 <https://github.com/wagtail/wagtail-autocomplete/pull/45>`_)

0.3 Release
-----------

* Various improvements to Tox testing and CI setup.
* Various improvements to Webpack compilation.
* Replace ``page_type`` keyword argument with more accurate ``target_model`` keyword argument. The old argument still works, but is deprecated.
* Enable autocomplete panel to run its javascript function when it is added to the page dynamically. This allows autocomplete panels to function inside of inline panels.
* Change references from model IDs to model PKs to allow panel compatibility with custom and non-integer primary keys.
