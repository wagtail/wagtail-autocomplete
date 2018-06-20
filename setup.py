from setuptools import setup, find_packages
from os import path
from wagtailautocomplete import __version__

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()


setup(
    name='wagtail-autocomplete',
    version=__version__,

    packages=find_packages(),
    include_package_data=True,

    description='An Autocomplete edit handler for Pages, Snippets, and more.',
    long_description=long_description,

    url='https://github.com/wagtail/wagtail-autocomplete',

    author='Emily Horsman and Harris Lapiroff',
    author_email='me@emilyhorsman.com',

    license='BSD-3-Clause',

    install_requires=[
        'wagtail>=1.11',
    ],

    extras_require={
        'docs': [
            'Sphinx>=1.7',
            'sphinx_rtd_theme>=0.4.0',
        ],
        'test': [
            'tox',
            'pytest>=3.5',
            'pytest-django>=3.2',
            'beautifulsoup4>=4.6.0',
            'html5lib>=0.999999999',
            'pytest-pythonpath>=0.7.2',
        ],
    },

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
        'Framework :: Wagtail',
        'Framework :: Wagtail :: 1',
        'Framework :: Wagtail :: 2',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
