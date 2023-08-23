import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Load pre-processed dataframe including both Pyroscience and SMB data
df = pd.read_csv("./data/processing/optode/A07_uws_match_pyroscience_smb.csv")

# Create datenum column
df["datenum"] = mdates.date2num(df["date_time"])

# === pH
# Create figure
fig, ax = plt.subplots(dpi=300, figsize=(6, 4))
      
ax.scatter(df["datenum"],
           df["pH"],
           s=1,
           alpha=0.4,
           c="k",
           edgecolor="none",
           zorder=1)

ax.set_title("pH")

# Save plot
plt.tight_layout()
plt.savefig("./figs/P01_plot_pH.png", dpi=300)

# === SALINITY
# Create figure
fig, ax = plt.subplots(dpi=300, figsize=(6, 4))
      
ax.scatter(df["datenum"],
           df["SBE45_sal"],
           s=1,
           alpha=0.4,
           c="k",
           edgecolor="none",
           zorder=1)

ax.set_title("salinity")

# Save plot
plt.tight_layout()
plt.savefig("./figs/P01_plot_sal.png", dpi=300)

# === TEMPERATURE
# Create figure
fig, ax = plt.subplots(dpi=300, figsize=(6, 4))
      
ax.scatter(df["datenum"],
           df["SBE38_water_temp"],
           s=1,
           alpha=0.4,
           c="k",
           edgecolor="none",
           zorder=1)

ax.set_title("temperature")

# Save plot
plt.tight_layout()
plt.savefig("./figs/P01_plot_temp.png", dpi=300)