# Figurex
Make figures with context managers in python: quicker, simpler, more readable. 


```python
with Figure() as ax:
    ax.plot([1,2],[3,4])
```


## Idea 

Tired of lengthy matplotlib code just for simple plotting? 
```python
# How plotting used to be:
import matplotlib.pyplot as plt

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
# How plotting becomes with figurex:
from figurex import Figure, Panel

with Figure("My plot", layout=(1,2), size=(4,5), save="file.png"):
    with Panel() as ax:
        ax.plot([1,2],[3,4])
    with Panel() as ax:
        ax.plot([2,3],[4,5])
```
The `Figure()` environment generates the `matplotlib`-based figure and axes for you, and automatically shows, saves, and closes the figure when leaving the context. It is just a wrapper around standard matplotlib code, you can use `ax` to modify the plot as you would normally do. Extend it your way without limits!

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
with Figure("Tea party", show=False):
    with Panel() as ax:
        ax.plot([5,5],[6,4])
my_figure = Figure.as_object()
# <_io.BytesIO at 0x...>
```

Plotting maps:
```python
from figurex import Basemap

with Figure(size=(3,3)):
    with Basemap("Germany", extent=(5,15,46,55), tiles="relief") as Map:
        x,y = Map(12.385, 51.331)
        Map.scatter(x, y,  marker="x", color="red", s=200)
```    
    
- Check out the [Examples Notebook](https://github.com/mschroen/figurex/blob/main/examples.ipynb)!

![Figurex examples](https://github.com/mschroen/figurex/blob/main/docs/figurex-examples.png)


## Install

```bash
pip install figurex
```

### Requirements

- Minimal requirements (basic plotting):
  - python >3.9
  - numpy
  - matplotlib
  - neatlogger (wrapper for loguru, logging)
- If you want to make geographic maps with figurex.cartopy:
  - cartopy
- If you want to make geographic maps with figurex.basemap:
  - basemap >1.4

## Related

- A discussion on [GitHub/matplotlib](https://github.com/matplotlib/matplotlib/issues/5218/) actually requested this feature long ago.
- The project [GitHub/contextplt](https://toshiakiasakura.github.io/contextplt/notebooks/usage.html) has implemented a similar concept.
