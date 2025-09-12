# Figurex
[![PyPi Version](https://img.shields.io/pypi/v/figurex.svg)](https://pypi.python.org/pypi/figurex/)
[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/mschroen/figurex/blob/main/LICENSE)
[![Read the Docs](https://readthedocs.org/projects/figurex/badge/?version=latest)](https://figurex.readthedocs.io/en/latest/?badge=latest)
[![Issues](https://img.shields.io/github/issues-raw/mschroen/figurex.svg?maxAge=25000)](https://github.com/mschroen/figurex/issues)  
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
from figurex.basemap import Basemap

with Figure(size=(3,3)):
    with Basemap("Germany", extent=(5,15,46,55), tiles="relief") as Map:
        x,y = Map(12.385, 51.331)
        Map.scatter(x, y,  marker="x", color="red", s=200)
```    
    
- Check out the [Examples Notebook](https://github.com/mschroen/figurex/blob/main/examples.ipynb)!

![Figurex examples](https://github.com/mschroen/figurex/blob/main/docs/figurex-examples.png)


## Documentation

A documentation and API reference can be found on [ReadTheDocs](https://figurex.readthedocs.io/en/latest):
- [Figure](https://figurex.readthedocs.io/en/latest/#figurex.figure.Figure) (context manager)
- [Panel](https://figurex.readthedocs.io/en/latest/#figurex.figure.Panel) (context manager)
- [Basemap](https://figurex.readthedocs.io/en/latest/#figurex.basemap.Basemap) (context manager)
- [Cartopy](https://figurex.readthedocs.io/en/latest/#figurex.cartopy.Cartopy) (context manager)

## Install

```bash
pip install figurex
```

If you want to use geospatial mapping features with [Basemap](https://pypi.org/project/basemap/) or [Cartopy](https://pypi.org/project/Cartopy/), install the corresponding optional features:
```bash
pip install figurex[basemap]
pip install figurex[cartopy]
```
If you work with `uv`, replace `pip install` by `uv add`.

### Requirements

- python >3.10
- numpy >2.0
- matplotlib >3.0
- basemap >=2.0 *(optional)*
- cartopy >=0.25 *(optional)*
- scipy *(optional, required by cartopy)*

## Related

- A discussion on [GitHub/matplotlib](https://github.com/matplotlib/matplotlib/issues/5218/) actually requested this feature long ago.
- The project [GitHub/contextplt](https://toshiakiasakura.github.io/contextplt/notebooks/usage.html) has implemented a similar concept.
