import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Import UWS continuous pH data
df = pd.read_csv("data/processing/optode/A10_uws_correct_pH.csv")

# Import subsamples
subsamples = pd.read_csv("data/_results/SO289_underway_TA_DIC_only_results.csv")

# Flag unrealistic subsamples for now (from S11)
subsamples["flag"] = 2
subsamples.loc[subsamples["date_time"]=="2022-03-04 15:35:00", "flag"] = 3
subsamples.loc[subsamples["date_time"]=="2022-03-29 18:30:00", "flag"] = 3
subsamples.loc[subsamples["date_time"]=="2022-03-25 05:25:00", "flag"] = 3

# Check that datetime colums are datetime objects
df["date_time"] = pd.to_datetime(df["date_time"])
subsamples["date_time"] = pd.to_datetime(subsamples["date_time"])

# Create datenum column
df["datenum"] = mdates.date2num(df["date_time"])
subsamples["datenum"] = mdates.date2num(subsamples["date_time"])

# === pH
# Create figure
fig, ax = plt.subplots(dpi=300, figsize=(6, 4))
      
ax.scatter(df["date_time"],
           df["pH_insitu_ta_est"],
           s=1,
           # alpha=0.4,
           c="g",
           label="$pH_{optode-raw}$",
           edgecolor="none",
           zorder=1)

ax.scatter(df["date_time"],
           df["pH_optode_corrected"],
           s=1,
           # alpha=0.4,
           c="k",
           label="$pH_{optode-corr}$",
           edgecolor="none",
           zorder=1)

ax.scatter(subsamples["date_time"],
           subsamples["pH_total_est_TA_DIC"],
           s=20,
           # alpha=0.4,
           c="b",
           label="$pH_{subsamples}$",
           edgecolor="none",
           zorder=1)

L = subsamples["flag"]==3
ax.scatter(subsamples[L]["date_time"],
           subsamples[L]["pH_total_est_TA_DIC"],
           s=20,
           # alpha=0.4,
           c="xkcd:red",
           label="$pH_{subsamples-BAD}$",
           edgecolor="none",
           zorder=1)

# Improve plot
plt.gca().xaxis.set_minor_locator(mdates.MonthLocator(bymonth=[2,3,4]));
plt.xticks(rotation=30)

ax.grid(alpha=0.3)

lgnd = plt.legend(loc="upper left", ncols=2, scatterpoints=1, fontsize=10)
for handle in lgnd.legendHandles:
    handle.set_sizes([12])

ax.set_ylim(7.8, 8.2)

# Save plot
plt.tight_layout()
plt.savefig("./figs/P03_plot_corrected_pH.png", dpi=300)