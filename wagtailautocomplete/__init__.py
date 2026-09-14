from importlib.metadata import PackageNotFoundError, version


try:
    __version__ = version("wagtail-autocomplete")
except PackageNotFoundError:
    # Not installed as a package
    __version__ = "0.0.0"
