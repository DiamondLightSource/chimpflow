from importlib.metadata import version

__version__ = version("chimpflow")
del version

__all__ = ["__version__"]
