import numpy as np
import matplotlib.pyplot as plt
from figurex.figure import Figure, Panel

# Using Cartopy
import cartopy
import cartopy.io.img_tiles as cimgt
import cartopy.feature as cfeature


class Cartopy(Panel):
    """
    Context manager for figure panels with geographic capabilities.
    Like class Panel, but with more features and dependencies.

    Usage
    -----
    ```
    from figurex.cartopy import Cartopy
    import cartopy.crs as ccrs
    crs = ccrs.EuroPP()

    with Figure():
        with Cartopy(
            extent=[5,15,46,55],
            projection=crs,
            tiles="OSM",
            zoom=6,
            features=["rivers", "ocean", "countries"]
        ) as ax:
            ax.scatter(10,51, transform=ccrs.PlateCarree())
    ```
    """

    default_features = [
        "ocean",
        "coast",
        "continents",
        "countries",
        "rivers",
    ]
    default_features_kw = dict(
        ocean=dict(
            color="lightblue"
        ),  # workaround because ocean does not show up in pdf export
        coast=dict(color="black", linewidth=0.5),
        boundary=dict(fill_color="lightblue"),
        continents=dict(color="linen"),
        countries=dict(color="black", linewidth=0.5, linestyle="-"),
        rivers=dict(color="lightblue"),
        states=dict(color="green", linewidth=1),
    )
    default_grid_kw = dict(
        dashes=[1, 0], linewidth=0.1, labels=[1, 0, 0, 1], fontsize=7
    )

    def __init__(
        self,
        *args,
        projection=None,
        tiles: str = None,
        tiles_cache: bool = False,
        zoom: int = 10,
        features: list | None = None,
        features_kw: dict | None = dict(),
        grid=True,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.tiles = tiles
        self.tiles_cache = tiles_cache
        self.zoom = zoom
        self.grid = grid

        if projection == "PlateCarree" or projection == "flat":
            projection = cartopy.crs.PlateCarree()
        self.projection = projection

        if features is None:
            self.features = {
                k: self.__class__.default_features_kw[k]
                for k in self.__class__.default_features
            }
        else:
            self.features = {k: self.__class__.default_features_kw[k] for k in features}
        for fkw in features_kw:
            self.features[fkw] = features_kw[fkw]

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
                extent=self.extent,  # .ax.get_extent(),
                tiles=self.tiles,
                zoom=self.zoom,
                cache=self.tiles_cache,
            )
        self.set_features()
        self.set_grid()

        if self.title:
            self.set_title(self.ax, self.title)
        if self.spines:
            self.set_spines(self.ax, self.spines)
        # if self.grid:
        #     self.set_grid(self.ax, self.grid)
        # if self.extent or self.x_range or self.y_range:
        #     self.set_range(self.ax, self.extent, self.x_range, self.y_range)
        if self.colorbar:
            self.add_colorbar(self.ax, self.colorbar)

        # super().__exit__(type, value, traceback)

    def set_features(self):
        """
        Applies map features
        """
        for feature in self.features:
            if feature == "ocean":
                self.ax.add_feature(cfeature.OCEAN, **self.features[feature])
            if feature == "coast":
                self.ax.add_feature(cfeature.COASTLINE, **self.features[feature])
            # if feature == "boundary":
            #     self.ax.add_feature(**self.features[feature])
            if feature == "continents":
                self.ax.add_feature(cfeature.LAND, **self.features[feature])
            if feature == "countries":
                self.ax.add_feature(cfeature.BORDERS, **self.features[feature])
            if feature == "rivers":
                self.ax.add_feature(cfeature.RIVERS, **self.features[feature])
            # if feature == "states":
            #     self.ax.add_feature(**self.features[feature])

    def set_grid(self):
        """
        Applies x and y axis ranges or bounding box to axis.
        """
        gls = self.ax.gridlines(draw_labels=True, alpha=0.4)
        gls.top_labels = False  # suppress top labels
        gls.right_labels = False  # suppress right labels

    @staticmethod
    def update_projection(ax, projection="3d"):

        rows, cols, start, stop = ax.get_subplotspec().get_geometry()
        fig = plt.gcf()
        axesflat = np.array(fig.axes).flat
        axesflat[start].remove()
        axesflat[start] = fig.add_subplot(rows, cols, start + 1, projection=projection)
        return axesflat[start]

    def add_basemap(self, ax=None, extent=None, tiles="OSM", zoom=12, cache=False):
        """
        Add a basemap to a plot.

        Example:
            with Figure() as ax:
                ax.plot(x, y)
                add_basemap(ax, extent=[9, 11, 49, 51], tiles='OSM', zoom=12)
        """
        if tiles == "OSM" or tiles == "osm":
            request = cimgt.OSM(cache=cache)
        elif tiles == "GoogleTiles-street" or tiles == "google":
            request = cimgt.GoogleTiles(cache=cache, style="street")
        elif tiles == "GoogleTiles-satellite" or tiles == "satellite-google":
            request = cimgt.GoogleTiles(cache=cache, style="satellite")
        elif tiles == "QuadtreeTiles" or tiles == "satellite-ms":
            request = cimgt.QuadtreeTiles(cache=cache)
        elif (
            tiles == "Stamen-terrain" or tiles == "stamen-terrain" or tiles == "stamen"
        ):
            request = cimgt.Stamen(cache=cache, style="terrain")
        elif tiles == "Stamen-toner" or tiles == "stamen-toner":
            request = cimgt.Stamen(cache=cache, style="toner")
        elif tiles == "Stamen-watercolor" or tiles == "stamen-watercolor":
            request = cimgt.Stamen(cache=cache, style="watercolor")
        else:
            print(
                "! Requested map tiles are not known, choose on of: ",
                "osm, google, satellite-google, satellite-ms, stamen, stamen-toner, stamen-watercolor",
            )

        if (
            extent
            and len(extent) == 4
            and extent[0] < extent[1]
            and extent[2] < extent[3]
        ):
            self.ax.set_extent(extent)
            self.ax.add_image(request, zoom)
        else:
            print(
                "! Map extent is invalid, must be of the form: [lon_1, lon_2, lat_1, lat_2]"
            )
