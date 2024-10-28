import importlib.metadata

__version__ = importlib.metadata.version("figurex")

from .figure import Figure, Panel

# Following subpackages have additional dependencies
# from .basemap import Basemap
# from .cartopy import Cartopy
