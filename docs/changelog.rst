=========
Changelog
=========

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
