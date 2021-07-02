from importlib.metadata import version, PackageNotFoundError
from .maiconverter import main

try:
    __version__ = version("maiconverter")
except PackageNotFoundError:
    __version__ = "not installed"
