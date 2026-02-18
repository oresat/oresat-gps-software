"""GPS OLAF app."""

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0.0.0"  # package is not installed

__all__ = ["__version__"]
