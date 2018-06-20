from setuptools import setup, find_packages
from os import path


here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()


setup(
    name    = 'wagtail-autocomplete',
    version = '0.1.0',

    packages = find_packages(),

    description = 'An Autocomplete edit handler for Pages, Snippets, and more.',
    long_description = long_description,

    url = 'https://github.com/littleweaver/wagtail-autocomplete',

    author       = 'Emily Horsman',
    author_email = 'me@emilyhorsman.com',

    license = 'BSD-3-Clause',

    install_requires = [
        'wagtail>=1.11',
    ],

    extras_require = {
        'docs': ['Sphinx>=1.7'],
        'test': [
            'tox',
            'pytest>=3.5',
            'pytest-django>=3.2',
            'beautifulsoup4>=4.6.0',
            'html5lib>=0.999999999',
            'pytest-pythonpath>=0.7.2',
        ],
    },

    classifiers = [
        'Programming Language :: Python :: 3.5',
    ],
)
