# %%
import numpy as np
import matplotlib.pyplot as plt
from figurex.figure import Figure, Panel
import cartopy
import cartopy.io.img_tiles as cimgt

# %%
class GeoPanel(Panel):
    """
    Context manager for figure panels with geographic capabilities.
    Like class Panel, but with more features and dependencies.
    """

    def __init__(
        self,
        *args,
        projection = None,
        tiles: str = None,
        tiles_cache: bool = False, 
        zoom: int = 10,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
      
        self.tiles = tiles
        self.tiles_cache = tiles_cache
        self.zoom = zoom

        if projection=='PlateCarree' or projection=='flat':
            projection = cartopy.crs.PlateCarree()
        self.projection = projection
        
        # self.subplot_kw["projection"] = self.projection

    def __enter__(self):
        # Determine the next available axis and provide it.
        self.ax = Figure.get_next_axis()
        self.ax = self.update_projection(self.ax, self.projection)
        return self.ax

    def __exit__(self, type, value, traceback):
        
        if self.tiles:
            self.add_basemap(
                self.ax,
                extent=self.ax.get_extent(),
                tiles=self.tiles,
                zoom=self.zoom,
                cache=self.tiles_cache
            )  

        super().__exit__(type, value, traceback)


    @staticmethod
    def update_projection(ax, projection="3d"):

        rows, cols, start, stop = ax.get_subplotspec().get_geometry()
        fig = plt.gcf()
        axesflat = np.array(fig.axes).flat
        axesflat[start].remove()
        axesflat[start] = fig.add_subplot(rows, cols, start+1, projection=projection)
        return axesflat[start]
    
    @staticmethod
    def add_basemap(
        ax=None,
        extent=None,
        tiles='OSM',
        zoom=12,
        cache=False
    ):
        """
        Add a basemap to a plot.
        Example:
            with Figure() as ax:
                ax.plot(x, y)
                add_basemap(ax, extent=[9, 11, 49, 51], tiles='OSM', zoom=12)
        """
        if tiles == 'OSM' or tiles=='osm':
            request = cimgt.OSM(cache=cache)
        elif tiles == 'GoogleTiles-street' or tiles=='google':
            request = cimgt.GoogleTiles(cache=cache, style="street")
        elif tiles == 'GoogleTiles-satellite' or tiles=='satellite-google':
            request = cimgt.GoogleTiles(cache=cache, style="satellite")
        elif tiles == 'QuadtreeTiles' or tiles=='satellite-ms':
            request = cimgt.QuadtreeTiles(cache=cache)
        elif tiles == 'Stamen-terrain' or tiles=='stamen-terrain' or tiles=='stamen':
            request = cimgt.Stamen(cache=cache, style="terrain")
        elif tiles == 'Stamen-toner' or tiles=='stamen-toner':
            request = cimgt.Stamen(cache=cache, style="toner")
        elif tiles == 'Stamen-watercolor' or tiles=='stamen-watercolor':
            request = cimgt.Stamen(cache=cache, style="watercolor")
        else:
            print('! Requested map tiles are not known, choose on of: ',
                'osm, google, satellite-google, satellite-ms, stamen, stamen-toner, stamen-watercolor')
        
        if extent and len(extent)==4 and extent[0]<extent[1] and extent[2]<extent[3]:
            ax.set_extent(extent)
            ax.add_image(request, zoom)
        else:
            print('! Map extent is invalid, must be of the form: [lon_1, lon_2, lat_1, lat_2]')
