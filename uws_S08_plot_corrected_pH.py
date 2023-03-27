import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Import UWS continuous pH data
df = pd.read_csv('data/processing/uws_S07_correct_pH.csv')

# Import subsamples
subsamples = pd.read_csv('data/processing/sub_S02_calculate_pH_total.csv')

# Check that datetime colums are datetime objects
df['date_time'] = pd.to_datetime(df['date_time'])
subsamples['date_time'] = pd.to_datetime(subsamples['date_time'])

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
           c="r",
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

# Improve plot
plt.gca().xaxis.set_minor_locator(mdates.MonthLocator(bymonth=[2,3,4]));
plt.xticks(rotation=30)

ax.grid(alpha=0.3)

lgnd = plt.legend(loc="upper left", scatterpoints=1, fontsize=10)
for handle in lgnd.legendHandles:
    handle.set_sizes([12])

ax.set_ylim(7.8, 8.2)

# Save plot
plt.tight_layout()
plt.savefig("./figs/uws_S08_plot_corrected_pH.png", dpi=300)