import pandas as pd
from matplotlib import pyplot as plt
from cartopy import crs as ccrs, feature as cfeature

# Load pre-processed dataframe including both Pyroscience and SMB data
df = pd.read_csv("data/processing/optode/A10_uws_correct_pH.csv")

# Visualise the dataset
fig = plt.figure(dpi=300, figsize=(11, 4))
ax = fig.add_subplot(projection=ccrs.PlateCarree())

# Plot data points
ax.scatter(
    df["lon"],
    df["lat"],
    c="xkcd:blue",
    s=15,
    label="High-resolution continuous pH data",
    marker=".",
    zorder=1,
    transform=ccrs.PlateCarree()
)

# Add land areas
ax.add_feature(
    cfeature.NaturalEarthFeature(
        "physical", "land", "10m"
    ),
    facecolor="xkcd:dark grey",
    edgecolor="none",
)
ax.add_feature(
    cfeature.NaturalEarthFeature(
        "physical", "lakes", "10m"
    ),
    edgecolor="none",
)

# Axis settings
ax.set_extent([-180, 180, -80, 0]) # east west south north
ax.gridlines(alpha=0.3, draw_labels=True, crs=ccrs.PlateCarree())

# Save figure
plt.tight_layout()
plt.savefig("figs/P02_plot_data_geo_distrib.png", dpi=300, bbox_inches = 'tight', pad_inches=0.1)
