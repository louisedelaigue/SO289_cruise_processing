import pandas as pd
import matplotlib.pyplot as plt
from cartopy import crs as ccrs, feature as cfeature

# Load CTD data
df = pd.read_csv('data/SO289_CTD_data_final_temp.csv')

# Load GLODAPv2.2022 data
glodap = pd.read_csv('data/glodap/GLODAPv2.2022_Pacific_Ocean.csv', low_memory=False)

# Remove "G2" from GLODAP columns
glodap.columns = [c.replace("G2", "") for c in list(glodap.columns)]

# Keep GLODAP data corresponding to SO289 area
lat_max = df.Latitude.max()
lat_min = df.Latitude.min()
lon_max = df.Longitude.max()
lon_min = df.Longitude.min()

L = ((glodap.latitude < lat_max) 
     & (glodap.latitude > lat_min)
     & (glodap.longitude < lon_max)   
     & (glodap.longitude > lon_min) 
     )

glodap = glodap[L]

# Only keep good DIC and TA data
L = (glodap["tco2f"]==2) & (glodap["talkf"]==2)
glodap = glodap[L]

# Map location of scatterpoints
# Visualise the dataset
fig = plt.figure(dpi=300, figsize=(8, 4))
ax = fig.add_subplot(projection=ccrs.PlateCarree())

# Plot data points
ax.scatter(
    glodap["longitude"],
    glodap["latitude"],
    c="xkcd:black",
    s=10,
    label="GLODAPv2.2022",
    marker=".",
    zorder=1,
    transform=ccrs.PlateCarree()
)

L = (df["alkalinity"].notnull()) & (df["dic_corrected"].notnull())
ax.scatter(df["Longitude"][L],
            df["Latitude"][L],
            s=10,
             c="xkcd:cyan",
             label="$SO289_{VINDTA-corr}$",
             edgecolor="none",
             zorder=0)

L = (df["TA_only"].notnull()) & (df["DIC_only"].notnull())
ax.scatter(df["Longitude"][L],
            df["Latitude"][L],
            s=10,
             c="xkcd:strawberry",
             label="$SO289_{QuAAtro}$",
             edgecolor="none",
             zorder=1)

# Add land areas
ax.add_feature(
    cfeature.NaturalEarthFeature(
        "physical", "land", "10m"
    ),
    facecolor="xkcd:dark grey",
    edgecolor="none",
)

# Axis settings
ax.set_extent([lon_min, lon_max, lat_min-50, lat_max+50]) # east west south noth
ax.gridlines(alpha=0.3, draw_labels=True, crs=ccrs.PlateCarree())

# Save figure
plt.tight_layout()
plt.savefig("./figs/ds_S03_compare_to_GLODAP_map.png", dpi=300)

# Scatter GLODAP and SO289 DIC
# Create figure
fig, ax = plt.subplots(ncols=2, dpi=300, figsize=(8, 4))

ax[0].scatter(glodap["tco2"],
              glodap["depth"],
              s=5,
              # alpha=0.4,
               c="k",
               label="GLODAPv2.2022",
               edgecolor="none",
               zorder=1)

ax[0].scatter(df["dic_corrected"],
              df["Depth"],
              s=5,
               c="xkcd:cyan",
               label="$SO289_{VINDTA-corr}$",
               edgecolor="none",
               zorder=1)

ax[0].scatter(df["DIC_only"],
              df["Depth"],
              s=5,
               c="xkcd:strawberry",
               label="$SO289_{QuAAtro}$",
               edgecolor="none",
               zorder=1)

ax[0].set_xlabel("DIC / μmol · kg$^\mathrm{-1}$")
ax[0].set_ylabel("Depth / m")

# Improve figure
ax[0].set_ylim(0, 6500)
ax[0].invert_yaxis()

# Scatter GLODAP and SO289 TA
# Create figure
ax[1].scatter(glodap["talk"],
              glodap["depth"],
              s=5,
              # alpha=0.4,
               c="k",
               label="GLODAPv2.2022",
               edgecolor="none",
               zorder=1)

ax[1].scatter(df["alkalinity"],
              df["Depth"],
              s=5,
               c="xkcd:cyan",
               label="$SO289_{VINDTA-corr}$",
               edgecolor="none",
               zorder=1)

ax[1].scatter(df["TA_only"],
              df["Depth"],
              s=5,
               c="xkcd:strawberry",
               label="$SO289_{QuAAtro}$",
               edgecolor="none",
               zorder=1)

# Improve figure
ax[1].set_ylim(0, 6500)
ax[1].invert_yaxis()

ax[1].set_xlabel("TA / μmol · kg$^\mathrm{-1}$")

ax[0].legend()

# Save plot
plt.tight_layout()
plt.savefig("./figs/ds_S03_compare_to_GLODAP.png", dpi=300)
