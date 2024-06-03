# %%
from figurex.figure import Figure, Panel

# %%
def test_Figure_single():
    with Figure("A simple plot", layout=(1,1)) as ax:
        ax.plot([1,2],[3,4])

test_Figure_single()

# %%
def test_Figure_grid():
    with Figure(layout=(1,2), grid="xy"):
        with Panel("a) Magic") as ax:
            ax.plot([1,2],[3,4])
        with Panel("b) Reality", grid="") as ax:
            ax.plot([5,5],[6,4])

test_Figure_grid()

# %%
def test_figure_memory():
    with Figure("For later", save="memory") as memory:
        with Panel("waff", grid="") as ax:
            ax.plot([5,5],[6,4])
    memory
test_figure_memory()

# %%
def test_Figure_mosaic():
    with Figure(layout=[[0,0,1],[2,3,1]], grid="xy"):
        with Panel("A") as ax:
            ax.plot([1,2],[3,4])
        with Panel("B", grid="") as ax:
            ax.plot([5,5],[6,4])
        with Panel("C", grid="") as ax:
            ax.plot([1,5],[6,4])
        with Panel("D", grid="x") as ax:
            ax.scatter([1,5,6,2,7,9],[6,4,9,5,1,4])

test_Figure_mosaic()

# %%
def test_Figure_extent():
    with Figure(layout=(1,2)):
        with Panel("a) Magic", x_range=(1,6)) as ax:
            ax.plot([1,2],[3,4])
        with Panel("b) Reality", extent=[4.9,5.1,3,7]) as ax:
            ax.plot([5,5],[6,4])
test_Figure_extent()

# %%
def test_Figure_datetime():
    
    import pandas
    from datetime import date, timedelta
    data = pandas.DataFrame()
    data["Apples"]  = [2,5,7,2,6,8,3,6,2,1]
    data["Oranges"] = [9,6,2,1,5,7,8,9,4,2]
    data.index = [date(2024,1,1)+timedelta(x*2) for x in range(10)]
    
    with Figure(
        layout=(2,1),
        x_major_ticks="weeks",
        x_major_fmt="%b %d",
        x_minor_ticks="days",
        gridspec_kw=dict(hspace=0.7)
    ):
        with Panel("a) Apples") as ax:
            ax.plot(data.index, data.Apples)
        with Panel("b) Oranges") as ax:
            ax.plot(data.index, data.Oranges)
test_Figure_datetime()
# %%
