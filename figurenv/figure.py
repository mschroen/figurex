# %%
import os
import io
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import YearLocator, MonthLocator, DayLocator, WeekdayLocator, HourLocator, MinuteLocator, DateFormatter

import cartopy
import cartopy.io.img_tiles as cimgt

class Figure:
    """
    Usage:
        # Map
        with Figure(size=(10,8), projection='flat',
                tiles='satellite', zoom=16) as ax:

        c = ax.scatter( data.lon, data.lat, c=data[var],
                    cmap='Spectral', vmin=0.07, vmax=0.18, 
                    s=100, edgecolor='k')
        add_colorbar(ax=ax, points=c, label='Soil moisture (g/g)',
                        bar_kw=dict(shrink=0.5, pad=0.02, aspect=20),
                        ticks=[0.07,0.09,0.12], ticklabels=["1","2","3"])
        
        # Layout regular grid
        with Figure(layout=(2,2)) as axes:
            axes[0][0].plot(x,y)
            axes[0][1].plot(x,y)
            axes[1][0].plot(x,y)
            axes[1][1].plot(x,y)

        # Layout with complex mosaic
        with Figure(title="My grid",
            layout = [[0,0,1],[2,'.',1]],
            gridspec_kw=dict(width_ratios=[1.4, 1, 1], height_ratios=[1, 2]),
            ) as axes:
            axes[0].plot(x,y)
            axes[1].plot(x,y)
            axes[2].plot(x,y)
                        
    """

    buff = None

    def __init__(self, title='', layout=(1,1), size=(11.69,8.27), abc=False,
                 gridspec_kw={}, save=None, save_dpi=250, format=None, fig=None,
                 transparent=True, projection=None, show=True, grid=False,
                 spines=None,
                 x_major_ticks=None, x_minor_ticks=None, x_major_fmt=None, x_minor_fmt=None,
                 x_ticks_last=False, tiles=None, zoom=10, tiles_cache=False, extent=None,
                 tick_steps=None, verbose=False):
        
        self.layout = layout
        self.size   = size
        self.title  = title
        self.abc    = abc
        self.gridspec_kw = gridspec_kw
        self.grid = grid
        self.spines = spines
        self.save   = save
        self.save_dpi = save_dpi
        self.format = format
        self.buff = io.BytesIO()
        self.transparent = transparent
        self.extent = extent
        if projection=='PlateCarree' or projection=='flat':
            projection = cartopy.crs.PlateCarree()
        self.projection = projection
        self.tick_steps = tick_steps
        
        self.tiles = tiles
        self.tiles_cache = tiles_cache
        self.zoom = zoom
        
        self.show = show
        if not show:
            plt.ioff()

        self.x_major_ticks = x_major_ticks
        self.x_minor_ticks = x_minor_ticks
        self.x_major_fmt = x_major_fmt
        self.x_minor_fmt = x_minor_fmt
        self.x_ticks_last = x_ticks_last

        self.verbose = verbose
        
    # Entering `with` statement
    def __enter__(self):
        
        return_later = None

        if isinstance(self.layout, tuple):
            """
            Regular grids, like (2,4)
            """
            self.fig, self.axes = plt.subplots(
                self.layout[0], self.layout[1],
                figsize = self.size,
                gridspec_kw = self.gridspec_kw,
                subplot_kw = dict(projection=self.projection)
                )
            if self.layout[0]==1 and self.layout[1]==1:
                self.axesflat = [self.axes]
                return_later = self.axes
            else:
                self.axesflat = self.axes.flatten()
                return_later = self.axesflat
        
        elif isinstance(self.layout, list):
            """
            Complex mosaic, like [[0,0,1],[2,'.',1]]
            """
            self.fig, self.axes = plt.subplot_mosaic(
                self.layout,
                layout="constrained",
                gridspec_kw = self.gridspec_kw,
                figsize = self.size,
                subplot_kw = dict(projection=self.projection)
                )
            # Convert labeled dict to list
            self.axesflat = [v for k, v in sorted(self.axes.items(), key=lambda pair: pair[0])]
            return_later = self.axesflat
                            
        for ax in self.axesflat:
            if self.extent:
                ax.set_xlim(self.extent[0], self.extent[1])
                ax.set_ylim(self.extent[2], self.extent[3])
        self.fig.suptitle(self.title)

        if self.save == "buff":
            if self.verbose:
                print("Figure instance returned. Usage: `with Figure(...) as F:`, `ax = F.ax`, `buff=F.buff`")
            return(self)
        else:
            return(return_later) # makes possibe: with Fig() as ax: ax.change

    # Exiting `with` statement
    def __exit__(self, type, value, traceback):

        if self.tiles:
            for ax in self.axesflat:
                add_basemap(ax, extent=ax.get_extent(),
                            tiles=self.tiles, zoom=self.zoom,
                            cache=self.tiles_cache)
                add_latlon_ticks(ax, steps=self.tick_steps)
                add_scalebar(ax,
                             color="k" if self.tiles in ["osm","google"] else "w")

        if self.abc:
            label_abc(self.axes, text=self.abc)

        for ax in self.axesflat:
            if self.grid:
                ax.grid(color="k", alpha=0.1)
            if self.spines:
                spines_label = dict(l="left", r="right", t="top", b="bottom")
                for s in "lrtb":
                    if s in self.spines:
                        ax.spines[spines_label[s]].set_visible(True)
                    else:
                        ax.spines[spines_label[s]].set_visible(False)

            set_time_ticks(ax, self.x_major_ticks, 'major',
                           fmt=None if self.x_ticks_last and ax!=self.axesflat[-1] else self.x_major_fmt)
            set_time_ticks(ax, self.x_minor_ticks, 'minor',
                           fmt=None if self.x_ticks_last and ax!=self.axesflat[-1] else self.x_minor_fmt)

        if self.save:
            if isinstance(self.save, str):
                
                if self.save == "buff":
                    self.save = self.buff
                    if self.format is None:
                        self.format = "svg"
                    matplotlib.use('Agg')
                else:
                    # Check and create folder
                    parent_folders = os.path.dirname(self.save)
                    if parent_folders and not os.path.exists(parent_folders):
                        os.makedirs(parent_folders)

                # Save and close single plot
                self.fig.savefig(self.save, format=self.format, bbox_inches='tight',
                    facecolor="none", dpi=self.save_dpi,
                    transparent=self.transparent)
                
            elif isinstance(self.save, matplotlib.backends.backend_pdf.PdfPages):
                self.save.savefig(self.fig)

            if self.save != "buff":
                plt.show()
            plt.close()

    def tight(self, ax=None, x=None, y=None, pad=(0, 0)):
        if ax is None:
            ax = self.axes
        ax.set_xlim(np.nanmin(x)-pad[0], np.nanmax(x)+pad[0])
        ax.set_ylim(np.nanmin(y)-pad[0], np.nanmax(y)+pad[0])

def add_basemap(ax=None, extent=None, tiles='OSM', zoom=12, cache=False):
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


def utm_from_lon(lon):
    """
    utm_from_lon - UTM zone for a longitude

    Not right for some polar regions (Norway, Svalbard, Antartica)

    :param float lon: longitude
    :return: UTM zone number
    :rtype: int
    """
    from math import floor
    return floor( ( lon + 180 ) / 6) + 1

def add_scalebar(ax, length=1, location=(0.89, 0.04),
              linewidth=1, color="w",
              units='km', m_per_unit=1000):
    """

    http://stackoverflow.com/a/35705477/1072212
    ax is the axes to draw the scalebar on.
    proj is the projection the axes are in
    location is center of the scalebar in axis coordinates ie. 0.5 is the middle of the plot
    length is the length of the scalebar in km.
    linewidth is the thickness of the scalebar.
    units is the name of the unit
    m_per_unit is the number of meters in a unit
    """
    # find lat/lon center to find best UTM zone
    x0, x1, y0, y1 = ax.get_extent(ax.projection.as_geodetic())
    # Projection in metres
    utm = ccrs.UTM(utm_from_lon((x0+x1)/2))
    # Get the extent of the plotted area in coordinates in metres
    x0, x1, y0, y1 = ax.get_extent(utm)
    if x1-x0>15000:
        length = 10
    elif x1-x0>1500:
        length = 1
    else :
        length = 0.1
    # Turn the specified scalebar location into coordinates in metres
    sbcx_1, sbcy_1 = x0 + (x1 - x0) * 0.95, y0 + (y1 - y0) * location[1]
    sbcx_2, sbcy_2 = x0 + (x1 - x0) * location[0], y0 + (y1 - y0) *(location[1]+0.01)
    sbcx_3, sbcy_3 = x0 + (x1 - x0) * location[0], y0 + (y1 - y0) *(location[1]-0.01)
    x_ur, y_ur = x0 + (x1 - x0) * 0.97, y0 + (y1 - y0) * 0.90
    # print(x_ur, y_ur)
    # Generate the x coordinate for the ends of the scalebar
    bar_xs = [sbcx_1 - length * m_per_unit, sbcx_1]
    
    # buffer for scalebar
    buffer = [matplotlib.patheffects.withStroke(linewidth=1, foreground=color)]
    # Plot the scalebar with buffer
    ax.plot(
        bar_xs, [sbcy_1, sbcy_1],
        transform=utm,
        color='k', linewidth=linewidth,
        path_effects=buffer)
    # buffer for text
    buffer = [matplotlib.patheffects.withStroke(linewidth=1, foreground=color)]
    
    # Plot the scalebar label
    t0 = ax.text(
        sbcx_1, sbcy_2, str(length) + ' ' + units,
        transform=utm,
        horizontalalignment='right', verticalalignment='bottom',
        color=color, zorder=2) #path_effects=buffer
    left = x0+(x1-x0)*0.03
    # Plot the N arrow
    t1 = ax.text(
        sbcx_1, y_ur, u'\u25B2\nN',
        transform=utm,
        horizontalalignment='right',
        verticalalignment='top',
        color=color, zorder=2)
    # Plot the scalebar without buffer, in case covered by text buffer
    ax.plot(bar_xs, [sbcy_1, sbcy_1], transform=utm,
            color=color,
        linewidth=linewidth, zorder=3)

def guess_ticks_from_lim(a, b, steps=None):
    import math
    import numpy as np
    if steps is None:
        diff = b-a
        magnitude = math.floor(math.log10(abs(diff)))
        round_digit = 10**(magnitude)
    else:
        round_digit = steps
    x_1 = round(float(a)/round_digit)*round_digit
    x_2 = round(float(b)/round_digit)*round_digit
    A = np.arange(x_1, x_2, round_digit)
    A = A[(A>=a) & (A<=b)]
    return A

def add_latlon_ticks(ax, steps=0.01, grid=True):
    
    # x_1 = round(float(a)/steps)*steps
    # x_2 = round(float(b)/steps)*steps
    # A = np.arange(x_1, x_2, steps)
    # A[(A>=a) & (A<=b)]

    extent = ax.get_extent()
    xs = guess_ticks_from_lim(extent[0], extent[1], steps)
    ys = guess_ticks_from_lim(extent[2], extent[3], steps)
    ax.set_xticks(xs)
    ax.set_yticks(ys)
    xlabels = np.array(["%.3f°" % x for x in xs])
    if len(xlabels) > 7:
        xlabels[1::3] = ""
        xlabels[2::3] = ""
    ylabels = np.array(["%.3f°" % y for y in ys])
    if len(ylabels) > 7:
        ylabels[1::3] = ""
        ylabels[2::3] = ""
    ax.set_xticklabels(xlabels)
    ax.set_yticklabels(ylabels)
    ax.set_xlabel(None)#'Longitude (°E)')
    ax.set_ylabel(None)#'Latitude (°N)')
    if grid:
        ax.grid(color='k', alpha=0.1)


def add_circle(ax, x, y, radius=1,
               fc='none', color='black',
               ls='-'):
    """
    Usage:
        add_circle(ax, x, y, r, "w", "k", "--")
    """
    circle = plt.Circle((x, y), radius,
                        fc=fc, color=color, ls=ls)
    ax.add_patch(circle)

def add_colorbar(ax=None, points=None, label=None,
            ticks=None, ticklabels=None,
            ticks_kw=dict(),
            bar_kw=dict(shrink=0.6, pad=0.02, aspect=20, extend="both"),
            label_kw=dict(rotation=270, labelpad=20),
            ):
            
    cb = plt.colorbar(points, ax=ax, **bar_kw)
    if not ticks is None:
        cb.ax.set_yticks(ticks)
    if not ticklabels is None:
        cb.ax.set_yticklabels(ticklabels, **ticks_kw)
    if not label is None:
        cb.set_label(label, **label_kw)

def set_time_ticks(ax=None, how=None, which='major', fmt=None):
    if how:
        if how=='minutes':
            how = MinuteLocator()
        if how=='hours':
            how = HourLocator()
        elif how=='days':
            how = DayLocator()
        elif how=='weeks':
            how = WeekdayLocator()
        elif how=='months':
            how = MonthLocator()
        elif how=='years':
            how = YearLocator()

        if which=='major':
            ax.xaxis.set_major_locator(how)
        elif which=='minor':
            ax.xaxis.set_minor_locator(how)
    if fmt:
        if which=='major':
            ax.xaxis.set_major_formatter(DateFormatter(fmt))
        elif which=='minor':
            ax.xaxis.set_minor_formatter(DateFormatter(fmt))

def add_rain(ax, data, color="C0", width=1,
             ymax=10, ylabel="Rain (mm)",
             color_axis=True, hide_axis=False
             ):
    ax2 = ax.twinx()
    ax2.bar(data.index, data.values,
            color=color, width=width)
    ax2.set_xlim(ax.get_xlim())
    ax2.set_ylim(0, ymax)
    ax2.set_ylabel(ylabel)
    if color_axis:
        ax2.yaxis.label.set_color(color)
        ax2.spines["right"].set_edgecolor(color)
        ax2.spines[["top","bottom", "left"]].set_visible(False)
        ax2.tick_params(axis='y', colors=color)
    if hide_axis:
        ax2.set_axis_off()
    ax.set_zorder(ax2.get_zorder() + 1)
    return(ax2)
