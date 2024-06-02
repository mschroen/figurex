# %%
from figurex.figure import Figure, Panel

# %%
def test_Figure_single():
    with Figure("nix", layout=(1,1)) as ax:
        ax.plot([1,2],[3,4])

test_Figure_single()

# %%
def test_Figure_grid():
    with Figure(layout=(1,2), grid="xy"):
        with Panel("wuff") as ax:
            ax.plot([1,2],[3,4])
        with Panel("waff", grid="") as ax:
            ax.plot([5,5],[6,4])

test_Figure_grid()

# %%
def test_figure_memory():
    with Figure("nix", save="memory") as memory:
        with Panel("waff", grid="") as ax:
            ax.plot([5,5],[6,4])
    memory
test_figure_memory()

# %%
