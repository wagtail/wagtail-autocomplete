============
Contributing
============

Wagtail Autocomplete is an open-source project and we welcome contributions! The eventual goal is to merge Wagtail Autocomplete into Wagtail core, so contributions should be made with that in mind.

We accept both issue reports and code contributions through our `GitHub repository <https://github.com/wagtail/wagtail/>`_.

Code Style
----------

This repo follows `Wagtail's guidelines <http://docs.wagtail.io/en/v1.11.1/contributing/index.html>`_.
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

The compiled documentation will now be in ``docs/_build/html``. Open this directory in a web browser to see it. Python comes with a module that makes it very easy to preview static files in a web browser. To start this simple server, run the following commands:

.. code-block:: sh

    # from insde of /path/to/wagtail-autocomplete/docs
    cd _build/html/
    python -m http.server 8080

Now you can open <http://localhost:8080/> in your web browser to see the compiled documentation.

Running the test suite
----------------------

This project uses ``pytest`` and ``tox`` to run its test suite. To install ``pytest`` and run the test suite, run:

.. code-block:: sh

    cd /path/to/wagtail-autocomplete
    pip install -e .[tests]
    pytest

To run the test suite against all dependency permutations, ensure that you have all the necessary Python interpreters installed and run:

.. code-block:: sh

    tox

If you make changes to test models, you must regenerate the migrations in ``wagtailautocomplete/tests/testapp/migrations/``. This can be a sort of tricky process and is left as an excercise to the reader until I'm able to standardize a mechanism for doing so. Since test models are ephemeral it is OK, and even preferable, to regenerate migrations from scratch for each change.
