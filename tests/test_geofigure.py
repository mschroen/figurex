## %%
# WIP
from figurex.figure import Figure, Panel
import matplotlib.pyplot as plt
from figurex.geo.figure import GeoPanel

# import cartopy
def test_geopanel(a=1, b=2):
    with Figure("nix", layout=(3,1)):
        print(plt.gcf().axes[0].get_subplotspec().get_geometry())
        with GeoPanel("Map", projection="flat", tiles="osm", zoom=11) as ax:
            ax.plot([12,12.1],[50,50.1])
        # with Panel("Map") as ax:
        print(plt.gcf().axes[0].get_subplotspec().get_geometry())
        with GeoPanel("_Map_", projection="flat", tiles="osm", zoom=11) as ax:
            ax.plot([12,12.1],[50,50.1])
        
        print(plt.gcf().axes[1].get_subplotspec().get_geometry())
test_geopanel()
# %%