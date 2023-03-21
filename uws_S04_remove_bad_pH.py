import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.dates as mdates

# Load pre-processed dataframe including both Pyroscience and SMB data
# df = pd.read_csv('./data/processing/preprocessing_uws_data.csv')
df = pd.read_csv('./data/processing/uws_S01_match_pyroscience_smb.csv')

# Create datenum column
df["datenum"] = mdates.date2num(df["date_time"])

# Remove first pH drop (prob due to optode not stabilizing)
L = df["datenum"] < 19050
df = df[~L]

# Remove second unrealistic pH increase
L = (df["datenum"] >  19052.1) & (df["datenum"] <  19052.64)
df = df[~L]

# Check points
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
plt.savefig("./figs/uws_S04_remove_bad_pH.png", dpi=300)

# Save post cleanup df
df.to_csv('./data/processing/uws_S04_remove_bad_pH.csv', index=False)