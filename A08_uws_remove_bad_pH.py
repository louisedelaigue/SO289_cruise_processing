# This script looks at massive pH drifts to remove bad pH data

import pandas as pd
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

# Create figure
fig, ax = plt.subplots(dpi=300, figsize=(6, 4))

ax.scatter(
    df["datenum"],
    df["pH"],
    s=1,
    alpha=0.4,
    c="k",
    label="good pH",
    edgecolor="none",
    zorder=1,
)

ax.scatter(
    raw["datenum"],
    raw["pH"],
    s=1,
    alpha=0.4,
    c="r",
    label="bad pH",
    edgecolor="none",
    zorder=0,
)

# Improve figure
ax.set_ylabel("pH")
ax.set_xlabel("time")

# Save plot
plt.tight_layout()
plt.savefig("./figs/A08_remove_bad_pH.png", dpi=300)

# Save post cleanup df
df.to_csv("./data/processing/optode/A08_remove_bad_pH.csv", index=False)
