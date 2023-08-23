# This script corrects continuous underway pH using an approach similar to
# the DIC drift correction, with a PCHIP through all pH difference
# in between pH(optode) and pH(subsamples), the latter calculated from
# TA/DIC 


import pandas as pd, numpy as np
from scipy.interpolate import PchipInterpolator
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

# Import UWS continuous pH data
df = pd.read_csv("./data/processing/optode/A09_estimate_alkalinity.csv")

# Import subsamples
subsamples = pd.read_csv("data/processing/vindta/SO289_underway_TA_DIC_only_results.csv")

# Flag unrealistic subsamples for now
subsamples["flag"] = 2
subsamples.loc[subsamples["date_time"] == "2022-03-04 15:35:00", "flag"] = 3
subsamples.loc[subsamples["date_time"] == "2022-03-29 18:30:00", "flag"] = 3
subsamples.loc[subsamples["date_time"] == "2022-03-25 05:25:00", "flag"] = 3

L = subsamples["flag"] == 2
subsamples = subsamples[L]

# Convert columns to datetime objects
df["date_time"] = pd.to_datetime(df["date_time"])
subsamples["date_time"] = pd.to_datetime(subsamples["date_time"])

# === SUBSAMPLES AND CONTINUOUS pH MATCH
# Reindex subsamples to match continuous pH data based on datetime
nearest = (
    df.set_index("date_time")
    .reindex(subsamples.set_index("date_time").index, method="nearest")
    .reset_index()
)

# Add continuous pH data points corresponding to subsamples
# based on date and time
point_location = subsamples["date_time"].tolist()
subsamples["pH_optode"] = np.nan
for location in point_location:
    subsamples.loc[subsamples["date_time"] == location, "pH_optode"] = subsamples[
        "date_time"
    ].map(nearest.set_index("date_time")["pH_insitu_ta_est"])

# === pH OFFSET CALCULATION
# Calculate offset between pH(TA/DIC) and pH(initial_alkalinity)
subsamples["offset"] = abs(subsamples["pH_total_est_TA_DIC"] - subsamples["pH_optode"])
offset = subsamples["offset"].mean()

subsamples["pH_corr"] = subsamples["pH_total_est_TA_DIC"] + offset

# Subtract pH(initial_alkalinity, corr) from pH(optode)
subsamples["diff"] = abs(subsamples["pH_total_est_TA_DIC"] - subsamples["pH_optode"])

# Remove where above difference is nan (PCHIP requirement)
L = subsamples["diff"].isnull()
subsamples = subsamples[~L]

# PCHIP difference points over date_time range in df
subsamples = subsamples.sort_values(by=["date_time"], ascending=True)
interp_obj = PchipInterpolator(
    subsamples["date_time"], subsamples["diff"], extrapolate=False
)
df["pchip_pH_difference"] = interp_obj(df["date_time"])

# === CORRECTION OF pH CONTINUOUS DATA
# Correct pH(optode) using PCHIP values - this depends on the filename
# because some points above or below subsamples
L = df["filename"] == "2022-02-24_221145_SO289"
df.loc[L, "pH_optode_corrected"] = df["pH_insitu_ta_est"] + df["pchip_pH_difference"]

L = df["filename"] == "2022-02-28_230025"
df.loc[L, "pH_optode_corrected"] = df["pH_insitu_ta_est"] + df["pchip_pH_difference"]

L = df["filename"] == "2022-03-24_003629_SO289_part_2"
df.loc[L, "pH_optode_corrected"] = df["pH_insitu_ta_est"] - df["pchip_pH_difference"]

# === SIMPLE MOVING AVERAGE
# Compute simple moving average (SMA) over period of 30 minutes
df["SMA"] = df["pH_optode_corrected"].rolling(60, min_periods=1).mean()

# Save to .csv
df.to_csv("data/processing/optode/A10_uws_correct_pH.csv", index=False)

# Save subsamples with raw optode pH to csv
subsamples.to_csv(
    "data/processing/optode/A10_uws_correct_pH_subsamples.csv", index=False
)

# Create figure
fig, ax = plt.subplots(dpi=300, figsize=(6, 4))

# Plot raw pH data
ax.scatter(
    df["date_time"],
    df["pH_insitu_ta_est"],
    label="Raw pH",
    color='blue',
    s=1,
    alpha=0.6
)

# Plot corrected pH data
ax.scatter(
    df["date_time"],
    df["pH_optode_corrected"],
    label="Corrected pH",
    color='black',
    s=1,
    alpha=0.4
)

# Scatter the subsamples for corrected pH
ax.scatter(
    subsamples["date_time"],
    subsamples["pH_total_est_TA_DIC"],
    label="Subsample $pH_{TA/DIC}$",
    color='red',
    s=3,
    marker="x",  # use different marker for clarity
    zorder=5  # to ensure it's on top
)

ax.set_title("Correction of pH time series based on recalculated pH from TA and DIC", fontsize=10)
ax.set_ylabel("$pH_{total}$")
ax.set_xlabel("Date")
ax.xaxis.set_major_locator(mdates.AutoDateLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
ax.tick_params(axis='both', which='major')
fig.autofmt_xdate()
ax.grid(alpha=0.3)

start_date = mdates.date2num(datetime.datetime.strptime("2022-02-22", "%Y-%m-%d"))
end_date = mdates.date2num(datetime.datetime.strptime("2022-04-06", "%Y-%m-%d"))

# Set the x-axis limits
ax.set_xlim(start_date, end_date)

# Add legend
ax.legend(loc='best', fontsize=10, markerscale=5)

# Save plot
plt.tight_layout()
plt.savefig("./figs/A10_uws_correct_pH.png", dpi=300)
