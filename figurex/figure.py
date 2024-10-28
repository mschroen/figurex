import os
import io
import numpy as np

# import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import (
    YearLocator,
    MonthLocator,
    DayLocator,
    WeekdayLocator,
    HourLocator,
    MinuteLocator,
    DateFormatter,
)


class Panel:
    """
    Context manager for figure panels. Inherited by class Figure.
    It looks for an active axis and applies basic settings.
    Provides the axis as context.
    """

    # Keyword arguments or Panels
    default_panel_kw = dict(
        spines="lb",
        grid="xy",
        x_range=None,
        y_range=None,
        extent=None,  # === bbox
        x_major_ticks=None,
        x_minor_ticks=None,
        x_major_fmt=None,
        x_minor_fmt=None,
        colorbar=None,
    )
    panel_kw = default_panel_kw

    def __init__(
        self,
        # Main
        title: str = "",
        spines: str = None,
        grid: str = None,
        # Axis
        x_range: tuple = None,
        y_range: tuple = None,
        extent: list = None,  # === bbox
        x_major_ticks: str = None,
        x_minor_ticks: str = None,
        x_major_fmt: str = None,
        x_minor_fmt: str = None,
        colorbar=None,
    ):
        # Set main properties
        self.title = title
        self.spines = spines
        self.grid = grid
        self.x_range = x_range
        self.y_range = y_range
        self.extent = extent
        self.x_major_ticks = x_major_ticks
        self.x_minor_ticks = x_minor_ticks
        self.x_major_fmt = x_major_fmt
        self.x_minor_fmt = x_minor_fmt
        self.colorbar = colorbar

        # Set properties from Panel kwarg (prio 1) or Figure kwarg (prio 2)
        if spines is None and "spines" in Panel.panel_kw:
            self.spines = Panel.panel_kw["spines"]
        if grid is None and "grid" in Panel.panel_kw:
            self.grid = Panel.panel_kw["grid"]
        if x_range is None and "x_range" in Panel.panel_kw:
            self.x_range = Panel.panel_kw["x_range"]
        if y_range is None and "y_range" in Panel.panel_kw:
            self.y_range = Panel.panel_kw["y_range"]
        if extent is None and "extent" in Panel.panel_kw:
            self.extent = Panel.panel_kw["extent"]
        if x_major_ticks is None and "x_major_ticks" in Panel.panel_kw:
            self.x_major_ticks = Panel.panel_kw["x_major_ticks"]
        if x_minor_ticks is None and "x_minor_ticks" in Panel.panel_kw:
            self.x_minor_ticks = Panel.panel_kw["x_minor_ticks"]
        if x_major_fmt is None and "x_major_fmt" in Panel.panel_kw:
            self.x_major_fmt = Panel.panel_kw["x_major_fmt"]
        if x_minor_fmt is None and "grid" in Panel.panel_kw:
            self.x_minor_fmt = Panel.panel_kw["x_minor_fmt"]

    def __enter__(self):
        # Determine the next available axis and provide it.
        self.ax = Figure.get_next_axis()
        return self.ax

    def __exit__(self, type, value, traceback):
        # Apply basic settings to simplify life.
        if self.title:
            self.set_title(self.ax, self.title)
        if self.spines:
            self.set_spines(self.ax, self.spines)
        if self.grid:
            self.set_grid(self.ax, self.grid)
        if self.extent or self.x_range or self.y_range:
            self.set_range(self.ax, self.extent, self.x_range, self.y_range)
        if self.x_major_ticks:
            self.set_time_ticks(
                self.ax, self.x_major_ticks, "major", fmt=self.x_major_fmt
            )
        if self.x_minor_ticks:
            self.set_time_ticks(
                self.ax, self.x_minor_ticks, "minor", fmt=self.x_minor_fmt
            )
        if self.colorbar:
            self.add_colorbar(self.ax, self.colorbar)

    @staticmethod
    def set_title(ax, text: str = "", fontsize: int = 10):
        """
        Set title of the panel, e.g.: a) Correlation

        Parameters
        ----------
        ax : matplotlib.axes._axes.Axes
            Axis to draw on.
        text : str, optional
            text for the title, by default ""
        fontsize : int, optional
            font size, by default 10
        """
        ax.set_title(text, loc="left", fontsize=str(fontsize))

    @staticmethod
    def set_grid(
        ax, dimension: str = "xy", color: str = "k", alpha: float = 1, **kwargs
    ):
        """
        Set grid

        Parameters
        ----------
        ax : matplotlib.axes._axes.Axes
            Axis to draw on.
        dimension : str, optional
            Dimension, e.g. x, y, or xy===both, by default "xy"
        color : str, optional
            Color of the grid lines, by default "k"
        alpha : float, optional
            Opacity of the lines, by default 1
        """
        if dimension == "xy":
            dimension = "both"

        ax.grid(axis=dimension, color=color, alpha=0.15, **kwargs)

    @staticmethod
    def set_spines(ax, spines: str = "lb"):
        """
        Show or hide axis spines

        Parameters
        ----------
        ax : matplotlib.axes._axes.Axes
            Axis to draw on.
        spines : str, optional
            Location of visible spines,
            a combination of letters "lrtb"
            (left right, top, bottom), by default "lb"
        """
        spines_label = dict(l="left", r="right", t="top", b="bottom")

        for s in "lrtb":
            if s in spines:
                ax.spines[spines_label[s]].set_visible(True)
            else:
                ax.spines[spines_label[s]].set_visible(False)

    @staticmethod
    def set_range(
        ax,
        extent=None,
        x_range: tuple = (None, None, None),
        y_range: tuple = (None, None, None),
    ):
        """
        Applies x and y axis ranges or bounding box to axis.

        Parameters
        ----------
        ax :
            Axis to change.
        extent : list or tuple, optional
            Bounding box [x0,x1,y0,y1], by default None
        x_range : tuple, optional
            tuple (x0,x1), by default (None,None)
        y_range : tuple, optional
            tuple (y0,y1), by default (None,None)
        """
        if extent:
            ax.set_xlim(extent[0], extent[1])
            ax.set_ylim(extent[2], extent[3])
        if isinstance(x_range, tuple):
            ax.set_xlim(x_range[0], x_range[1])
            if len(x_range) == 3:
                ax.set_xticks(np.arange(x_range[0], x_range[1], x_range[2]))
        if isinstance(y_range, tuple):
            ax.set_ylim(y_range[0], y_range[1])
            if len(y_range) == 3:
                ax.set_yticks(np.arange(y_range[0], y_range[1], y_range[2]))

    @staticmethod
    def set_time_ticks(ax=None, how: str = None, which: str = "major", fmt: str = None):
        """
        Format time axis.

        Parameters
        ----------
        ax , optional
            Axis to change, by default None
        how : str, optional
            Label every minutes, hours, days, weeks, months, or years, by default None
        which : str, optional
            Label major or minor ticks, by default "major"
        fmt : str, optional
            Format the date, e.g. "%b %d, %H_%M", by default None
        """
        if how:
            if how == "minutes":
                how = MinuteLocator()
            if how == "hours":
                how = HourLocator()
            elif how == "days":
                how = DayLocator()
            elif how == "weeks":
                how = WeekdayLocator()
            elif how == "months":
                how = MonthLocator()
            elif how == "years":
                how = YearLocator()

            if which == "major":
                ax.xaxis.set_major_locator(how)
            elif which == "minor":
                ax.xaxis.set_minor_locator(how)
        if fmt:
            if which == "major":
                ax.xaxis.set_major_formatter(DateFormatter(fmt))
            elif which == "minor":
                ax.xaxis.set_minor_formatter(DateFormatter(fmt))

    @staticmethod
    def add_colorbar(
        ax=None,
        points=None,
        label: str = None,
        ticks=None,
        ticklabels=None,
        ticks_kw: dict = dict(),
        bar_kw: dict = dict(shrink=0.6, pad=0.02, aspect=20, extend="both"),
        label_kw: dict = dict(rotation=270, labelpad=20),
    ):
        """
        Adds a color bar to the current panel.

        Parameters
        ----------
        ax  , optional
            Axis to draw on., by default None
        points , optional
            Line2D object to be described, by default None
        label : str, optional
            Axis label of the colorbar, by default None
        ticks : _type_, optional
            Ticks of the colorbar, by default None
        ticklabels : _type_, optional
            Tick labels, by default None
        ticks_kw : dict, optional
            Other tick keywords, by default dict()
        bar_kw : dict, optional
            Bar keywords, by default dict(shrink=0.6, pad=0.02, aspect=20, extend="both")
        label_kw : dict, optional
            Label keywords, by default dict(rotation=270, labelpad=20)
        """
        cb = plt.colorbar(points, ax=ax, **bar_kw)
        if not ticks is None:
            cb.ax.set_yticks(ticks)
        if not ticklabels is None:
            cb.ax.set_yticklabels(ticklabels, **ticks_kw)
        if not label is None:
            cb.set_label(label, **label_kw)

    @staticmethod
    def add_circle(ax, x, y, radius=1, fc="none", color="black", ls="-"):
        """
        Usage:
            add_circle(ax, x, y, r, "w", "k", "--")
        """
        circle = plt.Circle((x, y), radius, fc=fc, color=color, ls=ls)
        ax.add_patch(circle)


class Figure(Panel):
    """
    Context manager for Figures.
    It creates the figure and axes for the panels.
    Cares about saving and showing the figure in the end.
    Provides axes as context.
    """

    # When initiating Figure, no axis is active yet.
    # This will be incremented by Panel()
    current_ax = -1

    # If the Figure contains only one panel
    is_panel = True

    def __init__(
        self,
        # Main
        title: str = "",
        layout=(1, 1),  # tuple or lists
        size: tuple = (6, 3),
        save=None,  # str
        save_dpi: int = 250,
        save_format: str = None,
        transparent: bool = True,
        gridspec_kw: dict = dict(
            hspace=0.7, wspace=0.3
        ),  # wspace, hspace, width_ratios, height_ratios
        **kwargs
    ):
        # Set properties
        self.layout = layout
        self.size = size
        self.title = title
        self.save = save
        self.save_dpi = save_dpi
        self.save_format = save_format
        self.transparent = transparent

        self.subplot_kw = dict()
        self.gridspec_kw = gridspec_kw
        if "projection" in kwargs:
            self.subplot_kw = dict(projection=kwargs["projection"])

        # Reset default and set new panel arguments
        Panel.panel_kw = Panel.default_panel_kw.copy()
        for kw in Panel.panel_kw:
            if kw in kwargs:
                Panel.panel_kw[kw] = kwargs[kw]

        # Reset global axis counter
        Figure.current_ax = -1

        # If there is just one panel, behave as class Panel()
        Figure.is_panel = self.layout == (1, 1)
        if Figure.is_panel:
            super().__init__(title, **kwargs)

    def __enter__(self):
        # Create subplots with the given layout
        if isinstance(self.layout, tuple):
            self.ax = self.create_panel_grid()
        elif isinstance(self.layout, list):
            self.ax = self.create_panel_mosaic()

        # If it contains only one panel, behave like a Panel
        if Figure.is_panel:
            super().__enter__()

        # If save to memory, do not provide the axes but the memory handler instead
        # This is the only exception when Figure does not provide axes.
        if self.save == "memory":
            self.memory = io.BytesIO()
            return self.memory
        else:
            return self.ax

    def __exit__(self, type, value, traceback):

        # If it contains only one panel, behave like a Panel
        if Figure.is_panel:
            super().__exit__(type, value, traceback)
        else:
            self.fig.suptitle(self.title, y=1.02)

        if not self.save:
            pass

        elif self.save == "memory":
            # Save figure to memory, do not display
            self.fig.savefig(
                self.memory,
                format=self.save_format,
                bbox_inches="tight",
                facecolor="none",
                dpi=self.save_dpi,
                transparent=self.transparent,
            )
            plt.close()

        else:
            # Create folder if not existent
            parent_folders = os.path.dirname(self.save)
            if parent_folders and not os.path.exists(parent_folders):
                os.makedirs(parent_folders)

            # Save and close single plot
            self.fig.savefig(
                self.save,
                format=self.save_format,
                bbox_inches="tight",
                facecolor="none",
                dpi=self.save_dpi,
                transparent=self.transparent,
            )

    def create_panel_grid(self):
        # Regular grids, like (2,4)
        self.fig, self.axes = plt.subplots(
            self.layout[0],
            self.layout[1],
            figsize=self.size,
            gridspec_kw=self.gridspec_kw,
            subplot_kw=self.subplot_kw,
        )
        # Return a flat list of axes
        if self.layout[0] == 1 and self.layout[1] == 1:
            self.axes = [self.axes]
        else:
            self.axes = self.axes.flatten()
        return self.axes

    def create_panel_mosaic(self):
        # Make subplots
        self.fig, self.axes = plt.subplot_mosaic(
            self.layout,
            layout="constrained",
            figsize=self.size,
            # gridspec_kw = self.gridspec_kw,
            subplot_kw=self.subplot_kw,
        )
        # Convert labeled dict to list
        self.axes = [v for k, v in sorted(self.axes.items(), key=lambda pair: pair[0])]
        return self.axes

    @staticmethod
    def get_next_axis():
        """
        Get the next ax instance from the current figure

        Returns
        -------
        ax: matplotlib.axes._axes.Axes
            Matplotlib axis object which can be used for plotting
        """

        # List of axes in active figure
        axes_list = np.array(plt.gcf().axes)
        # Figure keeps track of the active axes index, increment it!
        if not Figure.is_panel:
            Figure.current_ax += 1
        # Return incremented active list element
        return axes_list[Figure.current_ax]

    @staticmethod
    def get_axes():
        """
        Get list of axes from the current figure.

        Usage
        -----
        for ax in Figure.get_axes():
            ax.set_ylim(0,1)

        Returns
        -------
        axes: numpy.array(matplotlib.axes._axes.Axes)
        """

        # List of axes in active figure
        axes_list = np.array(plt.gcf().axes)

        # Return
        return axes_list
