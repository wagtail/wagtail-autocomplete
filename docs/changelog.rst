=========
Changelog
=========

0.3 Release
-----------

* Various improvements to Tox testing and CI setup.
* Various improvements to Webpack compilation.
* Replace ``page_type`` keyword argument with more accurate ``target_model`` keyword argument. The old argument still works, but is deprecated.
* Enable autocomplete panel to run its javascript function when it is added to the page dynamically. This allows autocomplete panels to function inside of inline panels.
* Change references from model IDs to model PKs to allow panel compatibility with custom and non-integer primary keys.
