# figurex
Handy Figure generation with conteXt managers in python.

# Examples

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

# Related projects:

- A discussion on [GitHub/matplotlib](https://github.com/matplotlib/matplotlib/issues/5218/) actually requested this feature long ago.
- The project [GitHub/contextplt](https://toshiakiasakura.github.io/contextplt/notebooks/usage.html) has implemented a similar concept.