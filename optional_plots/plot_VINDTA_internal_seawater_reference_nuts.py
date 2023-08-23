import pandas as pd, numpy as np
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import itertools

# Import DBS file
dbs = pd.read_csv("data/processing/vindta/A02_process_SO289.csv")

# === PLOT NUTS FOR EACH "REAL" ANALYSIS DAY
# Prepare colours and markers
markers = itertools.cycle(("o", "^", "s", "v", "D", "<", ">"))
colors = itertools.cycle(
    (
        "xkcd:purple",
        "xkcd:green",
        "xkcd:blue",
        "xkcd:pink",
        "xkcd:deep blue",
        "xkcd:red",
        "xkcd:teal",
        "xkcd:orange",
        "xkcd:fuchsia",
    )
)

# Only keep nuts bottles that have file_good
L = (dbs["bottle"].str.startswith("NUTS")) & (dbs["file_good"] == True)
nuts = dbs[L]

# Only keep real analysis days
L = nuts["real_day"] == True
nuts = nuts[L]

real_days = list(nuts["dic_cell_id"].unique())

# Create a column with hours and minutes
nuts["analysis_datetime"] = pd.to_datetime(nuts["analysis_datetime"])
nuts["datetime"] = nuts["analysis_datetime"].dt.strftime("%H:%M")
nuts["datetime"] = pd.to_datetime(nuts["datetime"])

# Create figure
fig, ax = plt.subplots(dpi=300, figsize=(6, 4))

# Scatter NUTS DIC
for r in real_days:
    L = nuts["dic_cell_id"] == r
    data = nuts[L]
    m = next(markers)
    c = next(colors)
    l = r.split("_")[1].replace("-22", "")
    ax.scatter(
        x="datetime",
        y="dic",
        data=data,
        marker=m,
        color=c,
        alpha=0.3,
        label=l,
    )

    # Fit a polynomial
    a, b, d = np.polyfit(data["analysis_datenum"], data["dic"], 2)
    new_dic = a * (data["analysis_datenum"] ** 2) + b * (data["analysis_datenum"]) + d

    # Plot polynomial
    ax.plot(data["datetime"], new_dic, color=c, alpha=0.3)

myFmt = mdates.DateFormatter("%H")
ax.xaxis.set_major_formatter(myFmt)

ax.legend(loc="upper left", ncol=4)  # bbox_to_anchor=(1, 0.5)
# ax.set_ylim(2000, 2200)
ax.grid(alpha=0.3)
ax.set_xlabel("Time / hrs")
ax.set_ylabel("$DIC$ / μmol · $kg^{-1}$")

# Save plot
plt.tight_layout()
plt.savefig("./figs/vindta/day_nuts.png")