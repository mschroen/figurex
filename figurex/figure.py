import os
import io
import numpy as np
from neatlogger import log

import matplotlib
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

    Returns
    -------
    matplotlib.axes.Axes
        Provides the axis as context.

    Examples
    --------
    >>> with Figure(layout=(1,2)):
    ...    with Panel() as ax:
    ...        ax.plot([1,2], [3,4])
    ...    with Panel() as ax:
    ...        ax.plot([5,6], [7,8])
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
        extent: list | tuple = None,  # === bbox
        x_major_ticks: str = None,
        x_minor_ticks: str = None,
        x_major_fmt: str = None,
        x_minor_fmt: str = None,
        colorbar=None,
    ):
        """
        Initialises a Panel instance.

        Parameters
        ----------
        title: str, optional
            Title of the panel. Defaults to "", inheriting from the superior Figure.
        spines: str, optional
            Spines to show. The string may contain any of "lbtr" representing left, bottom, top, and right axis spines. Defaults to None, inheriting from the superior Figure.
        grid: str, optional
            Whether to show the grid. The string may contain any of "xy". Defaults to None, inheriting from the superior Figure.
        x_range: tuple, optional
            Range and tick steps of the x axis (from, to, steps). Defaults to None, inheriting from the superior Figure.
        y_range: tuple, optional
            Range and tick steps of the y axis (from, to, steps). Defaults to None, inheriting from the superior Figure.
        extent: list | tuple, optional
            Extent of the axes, providing a bounding box [x0, x1, y0, y1]. Defaults to None, inheriting from the superior Figure.
        x_major_ticks: str, optional
            Major x axis ticks for time serieses, can be hours, days, weeks, months, years. Defaults to None, inheriting from the superior Figure.
        x_minor_ticks: str, optional
            Minor x axis ticks for time serieses, can be hours, days, weeks, months, years. Defaults to None, inheriting from the superior Figure.
        x_major_fmt: str, optional
            Major x axis tick format, e.g. "%b %Y". Defaults to None, inheriting from the superior Figure.
        x_minor_fmt: str, optional
            Minor x axis tick format, e.g. "%b %Y". Defaults to None, inheriting from the superior Figure.
        colorbar: plot, optional
            Plot to be used for drawing a colorbar. Defaults to None, inheriting from the superior Figure.
        """
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

    def __enter__(self) -> matplotlib.axes.Axes:
        """
        When entering the context, return the current panel axis.

        Returns
        -------
        matplotlib.axes.Axes
            Axis object for the current panel.
        """
        # Determine the next available axis and provide it.
        self.ax = Figure.get_next_axis()
        return self.ax

    def __exit__(self, type, value, traceback):
        """
        When exiting the context, set additional axis properties.
        """
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
    def set_title(ax: matplotlib.axes.Axes, text: str = "", fontsize: int = 10):
        """
        Set title of the panel, e.g.: "a) Correlation"

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            Axis to draw on.
        text : str, optional
            text for the title, by default ""
        fontsize : int, optional
            font size, by default 10

        Examples
        --------
        >>> set_title(ax, "a) Correlation")
        """
        ax.set_title(text, loc="left", fontsize=str(fontsize))

    @staticmethod
    def set_grid(
        ax: matplotlib.axes.Axes,
        dimension: str = "xy",
        color: str = "k",
        alpha: float = 1,
        **kwargs
    ):
        """
        Set a grid for the axis.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            Axis to draw on.
        dimension : str, optional
            Dimension, e.g. x, y, or xy===both, by default "xy"
        color : str, optional
            Color of the grid lines, by default "k"
        alpha : float, optional
            Opacity of the lines, by default 1

        Examples
        --------
        >>> set_grid(ax, "xy")

        """
        if dimension == "xy":
            dimension = "both"

        ax.grid(axis=dimension, color=color, alpha=0.15, **kwargs)

    @staticmethod
    def set_spines(ax: matplotlib.axes.Axes, spines: str = "lb"):
        """
        Show or hide axis spines

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            Axis to draw on.
        spines : str, optional
            Location of visible spines,
            a combination of letters "lrtb"
            (left right, top, bottom), by default "lb"

        Examples
        --------
        >>> set_spines(ax, "lb")

        """
        spines_label = dict(l="left", r="right", t="top", b="bottom")

        for s in "lrtb":
            if s in spines:
                ax.spines[spines_label[s]].set_visible(True)
            else:
                ax.spines[spines_label[s]].set_visible(False)

    @staticmethod
    def set_range(
        ax: matplotlib.axes.Axes,
        extent: list | tuple = None,
        x_range: tuple = (None, None, None),
        y_range: tuple = (None, None, None),
    ):
        """
        Applies x and y axis ranges or bounding box to axis.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            Axis to change.
        extent : list | tuple, optional
            Bounding box [x0,x1,y0,y1], by default None
        x_range : tuple, optional
            tuple of either (x_min, x_max) or (x_min, x_max, x_steps), by default (None, None, None)
        y_range : tuple, optional
            tuple of either (y_min, y_max) or (y_min, y_max, y_steps), by default (None, None, None)

        Examples
        --------
        >>> set_range(ax, x_range=(0, 1, 0.1), y_range=(10, 20, 1))

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
    def set_time_ticks(
        ax: matplotlib.axes.Axes = None,
        how: str = None,
        which: str = "major",
        fmt: str = None,
    ):
        """
        Format time axis.

        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            Axis to change, by default None
        how : str, optional
            Label every minutes, hours, days, weeks, months, or years, by default None
            Can have a number at the start to indicate intervals
        which : str, optional
            Label major or minor ticks, by default "major"
        fmt : str, optional
            Format the date, e.g. "%b %d, %H_%M", by default None

        Examples
        --------
        >>> set_time_ticks(ax, "2weeks", "major", "%d\n%b)

        """
        import re

        match = re.match(r"(\d*)(.+)", how)
        if match:
            interval = match.group(1) or 1
            interval = int(interval)
            timestr = match.group(2)

        if how:
            if timestr == "minutes":
                locator = MinuteLocator(interval=interval)
            if timestr == "hours":
                locator = HourLocator(interval=interval)
            elif timestr == "days":
                locator = DayLocator(interval=interval)
            elif timestr == "weeks":
                locator = WeekdayLocator(interval=interval)
            elif timestr == "months":
                locator = MonthLocator(interval=interval)
            elif timestr == "years":
                locator = YearLocator(base=interval)

            if which == "major":
                ax.xaxis.set_major_locator(locator)
            elif which == "minor":
                ax.xaxis.set_minor_locator(locator)
        if fmt:
            if which == "major":
                ax.xaxis.set_major_formatter(DateFormatter(fmt))
            elif which == "minor":
                ax.xaxis.set_minor_formatter(DateFormatter(fmt))

    @staticmethod
    def add_colorbar(
        ax: matplotlib.axes.Axes = None,
        points=None,
        label: str = None,
        ticks: list | np.ndarray = None,
        ticklabels: list | np.ndarray = None,
        ticks_kw: dict = dict(),
        bar_kw: dict = dict(shrink=0.6, pad=0.02, aspect=20, extend="both"),
        label_kw: dict = dict(rotation=270, labelpad=20),
    ):
        """
        Adds a color bar to the current panel.

        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            Axis to draw on., by default None
        points , optional
            Line2D object to be described, by default None
        label : str, optional
            Axis label of the colorbar, by default None
        ticks : list, optional
            Ticks of the colorbar, by default None
        ticklabels : list, optional
            Tick labels, by default None
        ticks_kw : dict, optional
            Other tick keywords, by default dict()
        bar_kw : dict, optional
            Bar keywords, by default dict(shrink=0.6, pad=0.02, aspect=20, extend="both")
        label_kw : dict, optional
            Label keywords, by default dict(rotation=270, labelpad=20)

        Examples
        --------
        >>> points = ax.scatter([1,2], [3,4], c=[0.2,0.8], cmap="Spectral")
        ... add_colorbar(points, ax, label="Energy (eV)")

        """
        cb = plt.colorbar(points, ax=ax, **bar_kw)
        if not ticks is None:
            cb.ax.set_yticks(ticks)
        if not ticklabels is None:
            cb.ax.set_yticklabels(ticklabels, **ticks_kw)
        if not label is None:
            cb.set_label(label, **label_kw)

    @staticmethod
    def add_circle(
        ax: matplotlib.axes.Axes,
        x=0.0,
        y=0.0,
        radius: float = 1.0,
        fc: str = "none",
        color: str = "black",
        ls: str = "-",
    ):
        """
        Draws a circle on the plot.

        Parameters
        ----------
        ax: matplotlib.axes.Axes
            Axis object to draw on.
        x: x axis data type, optional
            Center x location of the circle.
        y: y axis data type, optional
            Center y location of the circle.
        radius: float, optional
            Radius of the circle. Defaults to 1.
        fc: str, optional
            Face color of the circle. Defaults to "none".
        color: str, optional
            Border color of the circle. Defaults to "black".
        ls: str, optional
            Line style of the circle. Defaults to "-".

        Returns
        -------
        ax
            Adds a circle patch to ax

        Examples
        --------
        >>> with Figure() as ax:
        ...    add_circle(ax, 1.5, 2.5, 1.0, "w", "k", "--")
        """
        circle = plt.Circle((x, y), radius, fc=fc, color=color, ls=ls)
        ax.add_patch(circle)


class Figure(Panel):
    """
    Context manager for Figures.
    It creates the figure and axes for the panels.
    Cares about saving and showing the figure in the end.
    Provides axes as context.

    Returns
    -------
    matplotlib.axes.Axes
        Provides the axis as context.

    Examples
    --------
    >>> with Figure() as ax:
    ...     ax.plot([1,2], [3,4])

    This is equivalent to:

    >>> with Figure():
    ...    with Panel() as ax:
    ...        ax.plot([5,6], [7,8])

    """

    # When initiating Figure, no axis is active yet.
    # This will be incremented by Panel()
    current_ax = -1
    current_fig = None

    # If the Figure contains only one panel
    is_panel = True

    def __init__(
        self,
        title: str = "",
        layout: tuple | list = (1, 1),
        size: tuple = (6, 3),
        save: str = None,
        save_dpi: int = 250,
        save_format: str = None,
        transparent: bool = True,
        gridspec_kw: dict = dict(hspace=0.7, wspace=0.3),
        backend: str = "",
        show: bool = True,
        **kwargs
    ):
        """
        Initialises the Figure instance.

        Parameters
        ----------
        title : str, optional
            Overarching Figure title, by default ""
        layout : tuple | list, optional
            Either a tuple (rows, columns) or a mosaic list of lists, e.g. [[1,2,3],[4,4,3]]. By default (1, 1)
        size : tuple, optional
            Defining the width and height of the figure, by default (6, 3)
        save : str, optional
            File name of the figure, by default None
        save_dpi : int, optional
            Dots per inch of the saved file, by default 250
        save_format : str, optional
            _description_, by default None
        transparent : bool, optional
            _description_, by default True
        gridspec_kw : dict, optional
            Keyword arguments to define the grid layout, could contain wspace, hspace, width_ratios, height_ratios. By default dict( hspace=0.7, wspace=0.3 )
        backend : str, optional
            _description_, by default ""
        show: bool, optional
            Whether or not to show the plot interactively, defaults to True
        """
        # Set properties
        self.layout = layout
        self.size = size
        self.title = title
        self.save = save
        self.save_dpi = save_dpi
        self.save_format = save_format
        self.transparent = transparent
        self.show = show

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

        if backend:
            # To plot into files, the agg backend must be used
            Figure.set_backend(backend)
            # import matplotlib.pyplot as plt # reload?

    def __enter__(self):
        """
        When entering the context, generate and return the plot axes.

        Returns
        -------
        matplotlib.axes.Axes
            One or a list of matplotlib.axes.Axes
        """
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
            log.warning(
                "Figure(save='memory') is deprecated, use Figure.as_object() instead."
            )
            # self.memory = io.BytesIO()
            # return self.memory

        return self.ax

    def __exit__(self, type, value, traceback):
        """
        Exits the context and saves the figure.
        """

        # If it contains only one panel, behave like a Panel
        if Figure.is_panel:
            super().__exit__(type, value, traceback)
        else:
            self.fig.suptitle(self.title, y=1.02)

        if not self.save:
            pass

        elif self.save == "memory":
            log.warning(
                "Figure(save='memory') is deprecated, use Figure.as_object() instead."
            )
            # Save figure to memory, do not display
            # self.fig.savefig(
            #     self.memory,
            #     format=self.save_format,
            #     bbox_inches="tight",
            #     facecolor="none",
            #     dpi=self.save_dpi,
            #     transparent=self.transparent,
            # )
            # plt.close()

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

        if self.show:
            plt.show()
        else:
            plt.close()

    @staticmethod
    def set_backend(backend: str):
        """
        Sets the current backend, e.g. "agg" to plot into a PDF file.
        If no interactive output is needed, use together with: Figure(show=False)

        Parameters
        ----------
        backend : str
            Matplotlib backend to be used, e.g.: "agg".

        Examples
        --------
        >>> Figure.set_backend("agg")
        ... with Figure(show=False) as ax:
        ...     ax.plot([1,2],[3,4])

        """
        matplotlib.use(backend)

    def create_panel_grid(self):
        """
        Creates a regular grid of axes.

        Returns
        -------
        List
            A flattened array of axes.

        Examples
        --------
        >>> with Figure(layout=(1,2)):
        ...     with Panel() as ax:
        ...         ax.plot([1,2],[3,4])
        ...     with Panel() as ax:
        ...         ax.plot([5,6],[7,8])

        """
        # Regular grids, like (2,4)
        try:
            self.fig, self.axes = plt.subplots(
                self.layout[0],
                self.layout[1],
                figsize=self.size,
                gridspec_kw=self.gridspec_kw,
                subplot_kw=self.subplot_kw,
            )
        except Exception as e:
            log.error(
                "An error occured while plotting the figure: {}",
                e,
            )
            if "KeyboardModifier" in str(e):
                log.warning(
                    "Make sure to set Figure.set_backend('agg') before plotting."
                )

        if self.fig:
            Figure.current_fig = self.fig
            # Return a flat list of axes
            if self.layout[0] == 1 and self.layout[1] == 1:
                self.axes = [self.axes]
            else:
                self.axes = self.axes.flatten()
            return self.axes
        else:
            return None

    def create_panel_mosaic(self):
        """
        Creates a mosaic layout from self.layout.

        Returns
        -------
        List of axes.
            The axes are sorted.

        Examples
        --------
        >>> with Figure(layout=[[1,2,2],[1,3,3]]):
        ...     with Panel() as ax:
        ...         ax.plot([1,2],[3,4])
        ...     with Panel() as ax:
        ...         ax.plot([5,6],[7,8])
        ...     with Panel() as ax:
        ...         ax.plot([9,0],[1,2])

        """
        # Make subplots
        try:
            self.fig, self.axes = plt.subplot_mosaic(
                self.layout,
                layout="constrained",
                figsize=self.size,
                # gridspec_kw = self.gridspec_kw,
                subplot_kw=self.subplot_kw,
            )
        except Exception as e:
            log.error(
                "Cannot create the figure: {}",
                e,
            )
            if "KeyboardModifier" in str(e):
                log.warning(
                    "Make sure to set Figure.set_backend('agg') before plotting."
                )
        # Convert labeled dict to list
        if self.fig:
            Figure.current_fig = self.fig
            self.axes = [
                v for k, v in sorted(self.axes.items(), key=lambda pair: pair[0])
            ]
            return self.axes
        else:
            return None

    @staticmethod
    def get() -> matplotlib.figure.Figure:
        """
        Get the current matplotlib figure instance.

        Returns
        -------
        matplotlib.figure.Figure
            The current figure instance.

        Examples
        --------
        >>> fig = Figure.get()

        """
        return Figure.current_fig

    @staticmethod
    def get_next_axis() -> matplotlib.axes.Axes:
        """
        Get the next ax instance from the current figure

        Returns
        -------
        matplotlib.axes.Axes
            Matplotlib axis object which can be used for plotting

        Examples
        --------
        >>> ax.plot([1,2],[3,4])
        ... ax = Figure.get_next_axis()
        ... ax.plot([5,6],[7,8])

        """

        # List of axes in active figure
        axes_list = np.array(Figure.get().axes)
        # Figure keeps track of the active axes index, increment it!
        if not Figure.is_panel:
            Figure.current_ax += 1
        # Return incremented active list element
        ax = axes_list[Figure.current_ax]
        return ax

    @staticmethod
    def get_axes() -> np.ndarray:
        """
        Get list of axes from the current figure.

        Returns
        -------
        numpy.ndarray of matplotlib.axes.Axes
            A list of axes objects

        Examples
        --------
        >>> for ax in Figure.get_axes():
        ...    ax.set_ylim(0,1)

        """

        # List of axes in active figure
        axes_list = np.array(plt.gcf().axes)

        # Return
        return axes_list

    @staticmethod
    def as_object(
        ax: matplotlib.axes.Axes = None,
        format: str = "png",
        tight: bool = True,
        facecolor: str = "none",
        dpi: int = 300,
        transparent: bool = True,
    ) -> io.BytesIO:
        """
        Saves a given figure as a BytesIO object. It can be later used as an input for fpdf2 images.

        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            Any axis of the figure to be saved, by default None (i.e., use latest axis)
        format : str, optional
            Figure storage format, can by "png", "svg", "pdf", by default "png". Notes: svg format sometimes has issues with colors, use png instead.
        tight : bool, optional
            Tight plotting without large padding, by default True
        facecolor : str, optional
            Background color of the figure, by default "none"
        dpi : int, optional
            Dots per inch of the figure, by default 300
        transparent : bool, optional
            Transparent background image, by default True

        Returns
        -------
        io.BytesIO
            An object that could be later used in PDFs, for instance.

        Examples
        -----
        >>> with Figure() as ax:
        ...     ax.plot([1,2], [3,4])
        ... my_figure = Figure.as_object()

        """
        obj = io.BytesIO()
        if ax is None:
            fig = Figure.get()
        else:
            fig = ax.get_figure()

        fig.savefig(
            obj,
            format=format,
            bbox_inches="tight" if tight else None,
            facecolor=facecolor,
            dpi=dpi,
            transparent=transparent,
        )
        return obj
