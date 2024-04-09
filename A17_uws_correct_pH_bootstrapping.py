import pandas as pd
import numpy as np
from scipy.interpolate import PchipInterpolator
import matplotlib.pyplot as plt
from brokenaxes import brokenaxes
import datetime

# Load data
df = pd.read_csv("./data/processing/optode/A09_estimate_alkalinity.csv")
subsamples_original = pd.read_csv("data/processing/vindta/SO289_underway_TA_DIC_only_results.csv")

# Pre-process data
df["filename"] = df["filename"].astype(str)
df["date_time"] = pd.to_datetime(df["date_time"])
subsamples_original["date_time"] = pd.to_datetime(subsamples_original["date_time"])

# Flag unrealistic subsamples for now
subsamples_original["flag"] = 2
subsamples_original.loc[subsamples_original["date_time"] == "2022-03-04 15:35:00", "flag"] = 3
subsamples_original.loc[subsamples_original["date_time"] == "2022-03-29 18:30:00", "flag"] = 3
subsamples_original.loc[subsamples_original["date_time"] == "2022-03-25 05:25:00", "flag"] = 3

L = subsamples_original["flag"] == 2
subsamples_original = subsamples_original[L]

# Calculate offsets for all subsamples
nearest = df.set_index("date_time").reindex(subsamples_original.set_index("date_time").index, method="nearest").reset_index()
subsamples_original["pH_optode"] = nearest["pH_insitu_ta_est"].values
subsamples_original["offset"] = subsamples_original["pH_total_est_TA_DIC"] - subsamples_original["pH_optode"]

# Function to apply conditional correction based on filename
def apply_correction(df_to_correct, subsamples):
    # Ensure 'offset' contains only finite values before interpolation
    subsamples = subsamples.dropna(subset=['offset'])
    subsamples = subsamples[np.isfinite(subsamples['offset'])]

    # Proceed only if there are enough points for interpolation
    if not subsamples.empty and len(subsamples) > 1:
        pchip_interp = PchipInterpolator(subsamples["date_time"].astype(np.int64), subsamples["offset"], extrapolate=False)
        
        # Iterate over the unique filenames in df and apply the correction based on the filename
        for filename in df_to_correct["filename"].unique():
            mask = df_to_correct["filename"] == filename
            if "2022-03-24_003629_SO289_part_2" in filename:
                df_to_correct.loc[mask, "pH_corrected"] = df_to_correct.loc[mask, "pH_insitu_ta_est"] - abs(pchip_interp(df_to_correct.loc[mask, "date_time"].astype(np.int64)))
            elif "2022-02-24_221145_SO289" in filename or "2022-02-28_230025" in filename:
                df_to_correct.loc[mask, "pH_corrected"] = df_to_correct.loc[mask, "pH_insitu_ta_est"] + abs(pchip_interp(df_to_correct.loc[mask, "date_time"].astype(np.int64)))
            else:
                df_to_correct.loc[mask, "pH_corrected"] = df_to_correct.loc[mask, "pH_insitu_ta_est"] + abs(pchip_interp(df_to_correct.loc[mask, "date_time"].astype(np.int64)))

    else:
        print("Not enough subsamples with finite 'offset' values for interpolation.")


## Apply "real" correction with all subsamples
apply_correction(df, subsamples_original)

# Parameters for bootstrapping
n_iterations = 100
fraction_to_omit = 0.5  # Fraction of subsamples to randomly omit

bootstrapped_ph_values = []

for iteration in range(n_iterations):
    subsamples = subsamples_original.sample(frac=1 - fraction_to_omit)
    subsamples = subsamples.sort_values(by="date_time")  # Ensure sorting by date_time
    df_iteration = df.copy()
    apply_correction(df_iteration, subsamples)
    bootstrapped_ph_values.append(df_iteration["pH_corrected"])

# Convert list to DataFrame for analysis
bootstrapped_ph_df = pd.DataFrame(bootstrapped_ph_values).T  # Transpose to align with df's indexing

# Calculate standard deviation for uncertainty
df["pH_uncertainty"] = bootstrapped_ph_df.std(axis=1)

# === SIMPLE MOVING AVERAGE
# Compute simple moving average (SMA) over period of 30 minutes
df["SMA"] = df["pH_corrected"].rolling(60, min_periods=1).mean()
df["SMA_uncertainty"] = df["pH_uncertainty"].rolling(60, min_periods=1).mean()

#%% === Plotting
# Create broken axes plot with adjusted spacing
fig = plt.figure(figsize=(6, 4), dpi=300)

start_break = datetime.datetime(2022, 3, 6)
end_break = datetime.datetime(2022, 3, 29)

# Set the limits for the left side of the broken x-axis
L = (df["SMA"].notnull()) & (df["date_time"] > datetime.datetime(2022, 3, 1, 15))
left_xlim = (df["date_time"][L].min(), start_break)

# Set the limits for the right side of the broken x-axis
right_xlim = (end_break, df["date_time"][L].max())

# Create broken axes plot with adjusted spacing and separate x-axis limits
bax = brokenaxes(xlims=(left_xlim, right_xlim), hspace=0.05, d=0, width_ratios=[2, 1], wspace=0.05)

L = df["SMA"].notnull()
bax.scatter(df["date_time"][L], df["pH_insitu_ta_est"][L], s=0.1, label="Original pH", alpha=0.6)
bax.scatter(df["date_time"][L], df["SMA"][L], s=0.1, label="Corrected pH", color='red', alpha=0.6)
bax.fill_between(df["date_time"][L], df["SMA"][L] - df["SMA_uncertainty"][L], df["SMA"][L] + df["SMA_uncertainty"][L], color='red', alpha=0.2, label="Uncertainty")
bax.scatter(subsamples_original["date_time"], subsamples_original["pH_total_est_TA_DIC"], color='k', label='Subsamples', s=6, alpha=0.6, edgecolor='black', zorder=5)

# Draw vertical lines at the break points
bax.axvline(start_break, color='black', linewidth=2)
bax.axvline(end_break, color='black', linewidth=2)

# Create right and top axis
bax2 = bax.twinx()[0]  # Get the first axes object from the list
bax3 = bax.twiny()[0]  # Get the first axes object from the list

bax2.set_ylabel('')
bax3.set_xlabel('')

# Hide the ticks and labels for the top and right axes
bax2.tick_params(axis='y', which='both', left=False, right=False, labelleft=False, labelright=False)
bax2.tick_params(axis='x', which='both', left=False, right=False, labelleft=False, labelright=False)

bax3.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False, labeltop=False)
bax3.tick_params(axis='y', which='both', bottom=False, top=False, labelbottom=False, labeltop=False)

# Hide the right and top spines
bax2.spines['right'].set_visible(False)
bax2.spines['left'].set_visible(False)
bax3.spines['bottom'].set_visible(False)
bax3.spines['top'].set_visible(False)

bax.set_ylabel("$pH_{total}$")
bax.set_ylim(7.9, 8.15)
bax.grid(alpha=0.3)
bax.legend(loc="upper left")
fig.autofmt_xdate()
