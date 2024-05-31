# %%
from figurenv import Figure

def test_figurenv():
    with Figure() as ax:
        ax.plot([1,2,3],[4,5,6])
    pass
test_figurenv()
# %%
