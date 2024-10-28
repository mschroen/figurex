# Figurex
Make figures with context managers in python: quicker, simpler, more readable.

## Idea 

Tired of lengthy matplotlib code just for simple plotting? 
```python
# How plotting used to be
import matplotlib.pyplot as pyplot

fig, axes = plt.subplots(1,2, figsize=(4,5))
plt.set_title("My plot")
ax = axes[0]
ax.plot([1,2],[3,4])
ax = axes[1]
ax.plot([2,3],[4,5])
fig.savefig("file.png", bbox_inches='tight')
plt.show()
```
Beautify your daily work with shorter and more readable code:
```python
# How plotting becomes with figurex
from figurex import Figure, Panel

with Figure("My plot", layout=(1,2), size=(4,5), save="file.png"):
    with Panel() as ax:
        ax.plot([1,2],[3,4])
    with Panel() as ax:
        ax.plot([2,3],[4,5])
```
It is just a wrapper around standard matplotlib code, extend it your way without limits!

## Examples

Make a simple plot:

```python
with Figure("A simple plot") as ax:
    ax.plot([1,2],[3,4])
```

A plot with two panels:
```python
with Figure(layout=(1,2), size=(6,3)):
    with Panel("a) Magic") as ax:
        ax.plot([1,2],[3,4])
    with Panel("b) Reality", grid="") as ax:
        ax.plot([5,5],[6,4])
```

Save a plot into memory for later use (e.g. in FPDF):
```python
with Figure("Tea party", save="memory") as memory:
    with Panel() as ax:
        ax.plot([5,5],[6,4])
memory
# <_io.BytesIO at 0x...>
```

Plotting maps:
```python
from figurex import Basemap

with Figure(size=(3,3)):
    with Basemap("Germany", extent=(5,15,46,55), tiles="relief") as Map:
        x,y = Map(12.385, 51.331)
        Map.scatter(x, y,  marker="x", zorder=20, color="r", s=200, lw=2)
```    
    
- Check out the [Examples Notebook](https://github.com/mschroen/figurex/blob/main/examples.ipynb)!



## Related projects:

- A discussion on [GitHub/matplotlib](https://github.com/matplotlib/matplotlib/issues/5218/) actually requested this feature long ago.
- The project [GitHub/contextplt](https://toshiakiasakura.github.io/contextplt/notebooks/usage.html) has implemented a similar concept.