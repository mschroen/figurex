
import importlib.metadata
__version__ = importlib.metadata.version("figurex")

from .figure import Figure, Panel
from .basemap import Basemap
from .cartopy import Cartopy