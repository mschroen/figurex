# %%
import numpy as np
from figurex.figure import Figure, Panel

# Using Basemap
from mpl_toolkits.basemap import Basemap as mplbasemap  # pip install basemap


class Basemap(Panel):
    """
    Context manager for figure panels with geographic capabilities.
    Like class Panel, but with more features and dependencies.

    Examples
    --------
    >>> from figurex.basemap import Basemap
    ... with Figure():
    ...     with Basemap(
    ...     extent=(5,15,46,55),
    ...     x_range=(5,15,3),
    ...     y_range=(47,56,2),
    ...     features = ["ocean", "countries", "rivers"],
    ...     tiles="relief"
    ... ) as Map:
    ...     x,y = Map(12.385, 51.331)
    ...     Map.scatter(x, y,  marker="x", zorder=20,)

    """

    default_features = [
        "ocean",
        "coast",
        "boundary",
        "continents",
        "countries",
        "rivers",
        "states",
    ]
    default_features_kw = dict(
        ocean=dict(
            land_color="lightblue", ocean_color="lightblue"
        ),  # workaround because ocean does not show up in pdf export
        coast=dict(color="black", linewidth=0.5),
        boundary=dict(fill_color="lightblue"),
        continents=dict(color="linen", lake_color="lightblue"),
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
        map_type: str = "normal",
        projection: str = "merc",  # merc cyl aeqd
        tiles: str = None,
        tiles_cache: bool = False,
        zoom: int = 1,
        center=None,
        resolution: str = "i",  # c, l, i, h, f
        anchor="NW",  # SW, S, SE, E, NE, N, NW, W
        suppress_ticks=False,
        grid_kw=None,
        features: list | None = None,
        features_kw: dict | None = dict(),
        epsg=None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.tiles = tiles
        self.tiles_cache = tiles_cache
        self.zoom = zoom

        self.bbox = self.extent
        # if projection=='PlateCarree' or projection=='flat':
        #     projection = cartopy.crs.PlateCarree()
        self.projection = projection
        self.resolution = resolution
        self.map_type = map_type
        self.epsg = epsg
        if grid_kw is None:
            self.grid_kw = self.__class__.default_grid_kw.copy()
        else:
            self.grid_kw = grid_kw

        self.anchor = anchor
        self.suppress_ticks = suppress_ticks

        if features is None:
            self.features = {
                k: self.__class__.default_features_kw[k]
                for k in self.__class__.default_features
            }
        else:
            self.features = {k: self.__class__.default_features_kw[k] for k in features}
        for fkw in features_kw:
            self.features[fkw] = features_kw[fkw]

        if center is None:
            if self.bbox is None:
                self.center = (10, 50)
            else:
                self.center = (self.bbox[0] - self.bbox[1], self.bbox[3] - self.bbox[2])

        # self.subplot_kw["projection"] = self.projection

    def __enter__(self):
        # Determine the next available axis and provide it.
        self.ax = Figure.get_next_axis()

        if self.map_type == "normal":

            self.Map = mplbasemap(
                llcrnrlon=self.extent[0],
                llcrnrlat=self.extent[2],
                urcrnrlon=self.extent[1],
                urcrnrlat=self.extent[3],
                lat_0=self.center[1],
                lon_0=self.center[0],
                # lat_ts=51.0
                resolution=self.resolution,
                projection=self.projection,
                # epsg=self.epsg,
                fix_aspect=True,
                anchor=self.anchor,
                ax=self.ax,
            )

            self.set_features()
            self.set_grid()

        elif self.map_type == "globe":

            self.Map = mplbasemap(
                projection="ortho",
                lat_0=self.center[1],
                lon_0=self.center[0],
                fix_aspect=True,
                anchor=self.anchor,
                ax=self.ax,
            )

            self.set_features()

            self.grid_kw["labels"] = [0, 0, 0, 0]
            if self.x_range is None:
                self.x_range = (-180, 180 + 1, 45)
            if self.y_range is None:
                self.y_range = (-90, 90 + 1, 30)
            self.set_grid()

        elif self.map_type == "world":

            if self.extent is None:
                self.extent = (-180, 180, -90, 90)

            self.Map = mplbasemap(
                projection="cyl",
                lat_0=self.center[1],
                lon_0=self.center[0],
                llcrnrlon=self.extent[0],
                llcrnrlat=self.extent[2],
                urcrnrlon=self.extent[1],
                urcrnrlat=self.extent[3],
                fix_aspect=True,
                anchor=self.anchor,
                ax=self.ax,
            )

            self.set_features()
            self.set_grid()

        # self.ax = self.update_projection(self.ax, self.projection)
        return self.Map

    def __exit__(self, type, value, traceback):

        if self.tiles == "marble":
            self.Map.bluemarble(scale=self.zoom)
        elif self.tiles == "relief":
            self.Map.shadedrelief(scale=self.zoom)
        elif self.tiles == "etopo":
            self.Map.etopo(scale=self.zoom)

        #     self.add_basemap(
        #         self.ax,
        #         extent=self.ax.get_extent(),
        #         tiles=self.tiles,
        #         zoom=self.zoom,
        #         cache=self.tiles_cache
        #     )

        # Apply basic settings to simplify life.
        if self.title:
            self.set_title(self.ax, self.title)
        if self.spines:
            self.set_spines(self.ax, self.spines)
        if self.colorbar:
            self.add_colorbar(self.ax, self.colorbar)

    def set_features(self):
        """
        Applies map features
        """
        for feature in self.features:
            if feature == "ocean":
                self.Map.drawlsmask(**self.features[feature])
            if feature == "coast":
                self.Map.drawcoastlines(**self.features[feature])
            if feature == "boundary":
                self.Map.drawmapboundary(**self.features[feature])
            if feature == "continents":
                self.Map.fillcontinents(**self.features[feature])
            if feature == "countries":
                self.Map.drawcountries(**self.features[feature])
            if feature == "rivers":
                self.Map.drawrivers(**self.features[feature])
            if feature == "states":
                self.Map.drawstates(**self.features[feature])

    def set_grid(self):
        """
        Applies x and y axis ranges or bounding box to axis.
        """
        # x
        if isinstance(self.x_range, tuple):
            self.Map.drawmeridians(
                np.arange(self.x_range[0], self.x_range[1], self.x_range[2]),
                **self.grid_kw
            )
        elif self.extent:
            self.Map.drawmeridians([self.extent[0], self.extent[1]], **self.grid_kw)
        # y
        if isinstance(self.y_range, tuple):
            self.Map.drawparallels(
                np.arange(self.y_range[0], self.y_range[1], self.y_range[2]),
                **self.grid_kw
            )
        elif self.extent:
            self.Map.drawparallels([self.extent[2], self.extent[3]], **self.grid_kw)
