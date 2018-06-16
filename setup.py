from setuptools import setup
from os import path


here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name    = 'wagtail-autocomplete',
    version = '0.1.0',

    packages = [
        'wagtailautocomplete',
    ],

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
    },

    classifiers = [
        'Programming Language :: Python :: 3.5',
    ],
)
