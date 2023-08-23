# This script looks at massive pH drifts to remove bad pH data

import pandas as pd
import datetime
from matplotlib import pyplot as plt
import matplotlib.dates as mdates

# Load pre-processed dataframe including both Pyroscience and SMB data
df = pd.read_csv("./data/processing/optode/A07_uws_match_pyroscience_smb.csv")
raw = df.copy()

# Create datenum column
df["datenum"] = mdates.date2num(df["date_time"])
raw["datenum"] = mdates.date2num(raw["date_time"])

# Remove first pH drop (prob due to optode not stabilizing)
L = df["datenum"] < 19047
df = df[~L]

# Remove second unrealistic pH increase
L = (df["datenum"] > 19052.2) & (df["datenum"] < 19052.64)
df = df[~L]

# Save post cleanup df
df.to_csv("./data/processing/optode/A08_remove_bad_pH.csv", index=False)

# Create figure
fig, ax = plt.subplots(dpi=300, figsize=(6, 4))

# Plot good pH data
ax.scatter(
    df["datenum"],
    df["pH"],
    s=1,
    alpha=0.4,
    c="black",
    label="Filtered pH",
    edgecolor="none",
    zorder=2,
)


# Plot bad pH data
ax.scatter(
    raw["datenum"],
    raw["pH"],
    s=1,
    alpha=0.4,
    c="red",
    label="Raw pH",
    edgecolor="none",
    zorder=1,
)

# Improve figure
ax.set_title(
    "Removal of unrealistic pH data points due to optode stabilization", fontsize=10
)
ax.set_ylabel("$pH_{total}$")
ax.set_xlabel("Date")
ax.xaxis.set_major_locator(mdates.AutoDateLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
ax.tick_params(axis="both", which="major")
fig.autofmt_xdate()
ax.grid(alpha=0.3)

start_date = mdates.date2num(datetime.datetime.strptime("2022-02-22", "%Y-%m-%d"))
end_date = mdates.date2num(datetime.datetime.strptime("2022-04-06", "%Y-%m-%d"))

# Set the x-axis limits
ax.set_xlim(start_date, end_date)

# Add legend
ax.legend(loc="lower right", fontsize=10, markerscale=5)

# Save plot
plt.tight_layout()
plt.savefig("./figs/A08_remove_bad_pH.png", dpi=300)
