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
