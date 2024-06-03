import os
import io
import numpy as np
import matplotlib
import matplotlib.pyplot as plt


class Panel:
    """
    Context manager for figure panels. Inherited by class Figure.
    It looks for an active axis and applies basic settings.
    Provides the axis as context.
    """

    # Keyword arguments or Panels 
    default_panel_kw = dict(
        spines = "lb",
        grid="xy",
        x_range = None,
        y_range = None,
        extent = None, # === bbox
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
        extent: list = None, # === bbox
    ):  
        # Set main properties
        self.title  = title
        self.spines = spines
        self.grid = grid
        self.x_range = x_range
        self.y_range = y_range
        self.extent = extent

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


    @staticmethod
    def set_title(
        ax,
        text: str = "",
        fontsize: int = 10
    ):
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
        ax.set_title(
            text,
            loc='left',
            fontsize=str(fontsize)
        )
                       
    
    @staticmethod
    def set_grid(
        ax,
        dimension: str = "xy",
        color: str = "k",
        alpha: float = 1,
        **kwargs
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

        ax.grid(
            axis=dimension,
            color=color,
            alpha=0.15,
            **kwargs
        )
    
    @staticmethod
    def set_spines(
        ax,
        spines: str = "lb"
    ):
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
        x_range: tuple = (None,None),
        y_range: tuple = (None,None)
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
        else:
            if isinstance(x_range, tuple):
                ax.set_xlim(x_range[0], x_range[1])
            if isinstance(y_range, tuple):
                ax.set_ylim(y_range[0], y_range[1])

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
        layout = (1,1), # tuple or lists
        size: tuple = (6,6),
        save = None, # str
        **kwargs
    ):
        # Set properties
        self.layout = layout
        self.size   = size
        self.title  = title
        self.save   = save

        self.subplot_kw = dict()
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
        Figure.is_panel = self.layout == (1,1)
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

        # Save figure to memory, do not display
        if self.save == "memory":
            self.fig.savefig(
                self.memory,
                format="svg",
                bbox_inches='tight',
                facecolor="none",
                dpi=250,
                transparent=True
            )
            plt.close()
            

    def create_panel_grid(self):
        # Regular grids, like (2,4)
        self.fig, self.axes = plt.subplots(
            self.layout[0],
            self.layout[1],
            figsize = self.size,
            # gridspec_kw = self.gridspec_kw,
            subplot_kw = self.subplot_kw 
        )
        # Return a flat list of axes 
        if self.layout[0]==1 and self.layout[1]==1:
            self.axes = [self.axes]
        else:
            self.axes = self.axes.flatten()
        return(self.axes)


    def create_panel_mosaic(self):
        # Make subplots
        self.fig, self.axes = plt.subplot_mosaic(
            self.layout,
            layout="constrained",
            figsize = self.size,
            # gridspec_kw = self.gridspec_kw,
            subplot_kw = self.subplot_kw 
        )
        # Convert labeled dict to list
        self.axes = [v for k, v in sorted(self.axes.items(), key=lambda pair: pair[0])]
        return(self.axes)
    
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


