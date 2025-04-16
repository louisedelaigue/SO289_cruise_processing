import pandas as pd
import numpy as np
from scipy.interpolate import PchipInterpolator
import matplotlib.pyplot as plt
from brokenaxes import brokenaxes
import datetime

# Load data
df = pd.read_csv("./data/processing/optode/A09_estimate_alkalinity.csv")
subsamples_original = pd.read_csv("data/processing/vindta/SO289_underway_TA_DIC_only_results_with_uncertainty.csv")

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
n_iterations = 1000
fraction_to_omit = 0.5  # Fraction of subsamples to randomly omit

bootstrapped_ph_values = []

for iteration in range(n_iterations):
    # Sample subsamples and introduce variability within RMSE
    sampled_subsamples = subsamples_original.sample(frac=1 - fraction_to_omit)
    sampled_subsamples['pH_total_est_TA_DIC_adjusted'] = sampled_subsamples['pH_total_est_TA_DIC'] + np.random.normal(0, sampled_subsamples['pH_RMSE'], size=len(sampled_subsamples))
    
    # Sort by date_time for consistent interpolation
    sampled_subsamples = sampled_subsamples.sort_values(by="date_time")
    
    # Perform pH correction using the adjusted pH values
    df_iteration = df.copy()
    apply_correction(df_iteration, sampled_subsamples)
    bootstrapped_ph_values.append(df_iteration["pH_corrected"])

# Convert list to DataFrame for analysis
bootstrapped_ph_df = pd.DataFrame(bootstrapped_ph_values).T  # Transpose to align with df's indexing

# Calculate RMSE for uncertainty
df["pH_uncertainty"] = np.sqrt((bootstrapped_ph_df.subtract(df["pH_corrected"], axis=0) ** 2).mean(axis=1))

# Save as csv
df.to_csv("data/processing/optode/A17_uws_correct_pH_bootstrapping_subsaomples_uncertainty.csv", index=False)

# === SIMPLE MOVING AVERAGE
# Compute simple moving average (SMA) over period of 30 minutes
df["SMA"] = df["pH_corrected"].rolling(60, min_periods=1).mean()
df["SMA_uncertainty"] = df["pH_uncertainty"].rolling(60, min_periods=1).mean()

# === Plotting
# Create broken axes plot with adjusted spacing
fig = plt.figure(figsize=(6, 4), dpi=300)

# Define start and end of the xaxis break
start_break = datetime.datetime(2022, 3, 6)
end_break = datetime.datetime(2022, 3, 29)

# Set the limits for the left side of the broken x-axis
L = (df["SMA"].notnull()) & (df["date_time"] > datetime.datetime(2022, 3, 1, 15))
left_xlim = (df["date_time"][L].min(), start_break)

# Set the limits for the right side of the broken x-axis
right_xlim = (end_break, df["date_time"][L].max())

# Create broken axes plot with adjusted spacing and separate x-axis limits
bax = brokenaxes(xlims=(left_xlim, right_xlim), hspace=0.05, d=0, width_ratios=[2, 1], wspace=0.05)

# Plot the stuff we're interested in
L = df["SMA"].notnull()
bax.scatter(df["date_time"][L], df["pH_insitu_ta_est"][L], s=0.1, label="Uncorrected pH", color='xkcd:light pink', alpha=0.6)
bax.scatter(df["date_time"][L], df["SMA"][L], s=0.1, label="Corrected pH", color='b', alpha=0.6)
bax.fill_between(df["date_time"][L], df["SMA"][L] - df["SMA_uncertainty"][L], df["SMA"][L] + df["SMA_uncertainty"][L], color='b', alpha=0.2)
bax.scatter(subsamples_original["date_time"], subsamples_original["pH_total_est_TA_DIC"], color='k', label='Subsamples $pH_{TA/DIC}$', s=20, alpha=0.6, edgecolor='k', zorder=6)

# Draw vertical lines at the break points
bax.axvline(start_break, color='k', linewidth=1.2)
bax.axvline(end_break, color='k', linewidth=1.2)

# === BELOW IS JUST TO MAKE THE PLOT LOOK PRETTY
# Create right and top axis
bax2 = bax.twinx()[0]  # Get the first axes object from the list
bax3 = bax.twiny()[0]  # Get the first axes object from the list

bax2.set_ylabel('')
bax3.set_xlabel('')

bax2.set_yticks([])
bax3.set_xticks([])

bax2.set_yticklabels([])
bax3.set_xticklabels([])

# Hide the right and top spines
# bax2.spines['right'].set_visible(False)
# bax2.spines['left'].set_visible(False)
# bax3.spines['bottom'].set_visible(False)
# bax3.spines['top'].set_visible(False)

# Now, loop through each subplot in your broken axis to adjust the labels
for ax in bax.axs:
    # Get all the current x-tick labels
    labels = ax.get_xticklabels()
    
    # Create a new list of labels, where you replace specific dates with an empty string
    new_labels = [label if label.get_text() != '2022-03-29' else '' for label in labels]
    
    # Set the modified list of labels back to the axis
    ax.set_xticklabels(new_labels)

# Add a legend
# Get handles and labels
handles, labels = ax.get_legend_handles_labels()

# Modify the properties of the first two legend handles
# Create custom legend artists with the desired marker scale
from matplotlib.lines import Line2D
custom_handles = [
    Line2D([0], [0], marker='o', color='w', label='Uncorrected pH', markersize=6, markerfacecolor='xkcd:light pink'),
    Line2D([0], [0], marker='o', color='w', label='Corrected pH', markersize=6, markerfacecolor='b'),
] + handles[2:]  # Append other handles without modification

# Create the legend with the custom handles
legend = bax.legend(handles=custom_handles, loc="upper left")

# Improve plot
bax.set_ylabel("$pH_{total}$")
bax.set_ylim(7.9, 8.15)
bax.grid(alpha=0.3)
fig.autofmt_xdate()

plt.savefig("./figs/SO289_pH_correction_with_uncertainty.png")
plt.show()

# === COMPARE UNCERTAINTY TO BOOTSTRAPPING ONLY
check = pd.read_csv("data/processing/optode/A17_uws_correct_pH_bootstrapping.csv")

# Assuming df and check have been loaded and processed correctly
# Define start and end of the x-axis break
start_break = datetime.datetime(2022, 3, 6)
end_break = datetime.datetime(2022, 3, 29)

# Create broken axes plot with adjusted spacing
fig = plt.figure(figsize=(10, 6), dpi=300)
bax = brokenaxes(xlims=[(df['date_time'].min(), start_break), (end_break, df['date_time'].max())],
                  d=0.05,  # Spacing between the broken parts
                  wspace=0.05,  # Width ratio between broken parts
                  despine=False)  # Hide the top and right frame lines

# Plot the pH uncertainty from 'df'
bax.scatter(df['date_time'], df['pH_uncertainty'], color='blue', label='New pH Uncertainty', s=2, alpha=0.6)

# Plot the pH uncertainty from 'check'
bax.scatter(check['date_time'], check['pH_uncertainty'], color='red', label='Old pH Uncertainty', s=2, alpha=0.6)

# Formatting
bax.set_xlabel('Date Time')
bax.set_ylabel('pH Uncertainty')
bax.legend(loc='upper right')
bax.grid(True)

# Draw vertical lines at the break points to indicate the break in the plot
bax.axvline(x=start_break, color='gray', linestyle='--')
bax.axvline(x=end_break, color='gray', linestyle='--')

# Adjust labels to avoid overlap and improve readability
plt.gcf().autofmt_xdate()

plt.show()

