import pandas as pd
import numpy as np
from scipy.interpolate import PchipInterpolator
import matplotlib.pyplot as plt
from brokenaxes import brokenaxes
import datetime
from matplotlib.lines import Line2D
from matplotlib import gridspec
import matplotlib.dates as mdates

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
n_iterations = 100
fraction_to_omit = 0.5  # Fraction of subsamples to randomly omit

bootstrapped_ph_values = []

for iteration in range(n_iterations):
    # Always include the first and last subsample
    first_subsample = subsamples_original.iloc[[0]]
    last_subsample = subsamples_original.iloc[[-1]]

    # Sample the remaining subsamples, excluding the first and last
    remaining_subsamples = subsamples_original.iloc[1:-1].sample(frac=1 - fraction_to_omit)

    # Combine the first, last, and remaining subsamples
    subsamples = pd.concat([first_subsample, remaining_subsamples, last_subsample])

    subsamples = subsamples.sort_values(by="date_time")  # Ensure sorting by date_time
    df_iteration = df.copy()
    apply_correction(df_iteration, subsamples)
    bootstrapped_ph_values.append(df_iteration["pH_corrected"])

# Convert list to DataFrame for analysis
bootstrapped_ph_df = pd.DataFrame(bootstrapped_ph_values).T  # Transpose to align with df's indexing

# Calculate standard deviation for uncertainty
df["pH_uncertainty"] = bootstrapped_ph_df.std(axis=1)

# Save as csv
df.to_csv("data/processing/optode/A17_uws_correct_pH_bootstrapping.csv", index=False)

# === SIMPLE MOVING AVERAGE
# Compute simple moving average (SMA) over period of 30 minutes
df["SMA"] = df["pH_corrected"].rolling(60, min_periods=1).mean()
df["SMA_uncertainty"] = df["pH_uncertainty"].rolling(60, min_periods=1).mean()


#%%# === Plotting only South Pacific
# Create broken axes plot with adjusted spacing
fig = plt.figure(figsize=(6, 4), dpi=300)

# Define start and end of the x-axis break
start_break = datetime.datetime(2022, 3, 6)
end_break = datetime.datetime(2022, 3, 24)

# Set the limits for the left side of the broken x-axis
L = (df["SMA"].notnull()) & (df["date_time"] > datetime.datetime(2022, 3, 1, 15))
left_xlim = (df["date_time"][L].min(), start_break)

# Set the limits for the right side of the broken x-axis
right_xlim = (end_break, df["date_time"][L].max())

# Create broken axes plot with adjusted spacing and separate x-axis limits
bax = brokenaxes(xlims=(left_xlim, right_xlim), hspace=0.05, d=0, width_ratios=[1, 2], wspace=0.05)

# Plot the stuff we're interested in
L = df["SMA"].notnull()
bax.scatter(df["date_time"][L], df["pH_insitu_ta_est"][L], s=0.1, label="Uncorrected pH", color='xkcd:light pink', alpha=0.6)
bax.scatter(df["date_time"][L], df["SMA"][L], s=0.1, label="Corrected pH", color='b', alpha=0.6)
bax.fill_between(df["date_time"][L], df["SMA"][L] - df["SMA_uncertainty"][L], df["SMA"][L] + df["SMA_uncertainty"][L], color='b', alpha=0.2)


# Before plotting, filter out subsamples that fall within the break period
mask = (subsamples_original["date_time"] < start_break) | (subsamples_original["date_time"] >= end_break)
filtered_subsamples = subsamples_original[mask]
# Now plot using the filtered subsamples
bax.scatter(filtered_subsamples["date_time"], filtered_subsamples["pH_total_est_TA_DIC"], color='k', label='Subsamples $pH_{TA/DIC}$', s=20, alpha=0.6, edgecolor='k', zorder=6)

# bax.scatter(subsamples_original["date_time"], subsamples_original["pH_total_est_TA_DIC"], color='k', label='Subsamples $pH_{TA/DIC}$', s=20, alpha=0.6, edgecolor='k', zorder=6)

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

# Hide the right and top spines and labels
# bax2.spines['right'].set_visible(False)
# bax2.spines['left'].set_visible(False)
# bax3.spines['bottom'].set_visible(False)
# bax3.spines['top'].set_visible(False)


# Now, loop through each subplot in your broken axis to adjust the labels
for ax in bax.axs:
    # Get all the current x-tick labels
    labels = ax.get_xticklabels()
    
    # Create a new list of labels, where you replace specific dates with an empty string
    new_labels = [label.get_text() if label.get_text() != '2022-03-23' else '' for label in labels]
    
    # Set the modified list of labels back to the axis
    ax.set_xticklabels(new_labels)

# Add a legend
# Get handles and labels
handles, labels = bax.get_legend_handles_labels()

# Modify the properties of the first two legend handles
# Create custom legend artists with the desired marker scale
custom_handles = [
    Line2D([0], [0], marker='o', color='w', label='Uncorrected pH', markersize=6, markerfacecolor='xkcd:light pink'),
    Line2D([0], [0], marker='o', color='w', label='Corrected pH', markersize=6, markerfacecolor='b'),
    Line2D([0], [0], marker='o', color='w', label='Subsamples $pH_{TA/DIC}$', markersize=6, markerfacecolor='k')
] + list(handles[2:])  # Append other handles without modification

# Create the legend with the custom handles
legend = bax.legend(handles=custom_handles, loc="upper center", bbox_to_anchor=(0.5, -0.3), ncol=3, fontsize=8)

# Improve plot
bax.set_ylabel("$pH_{total}$")
bax.set_ylim(7.9, 8.15)
bax.grid(alpha=0.3)
fig.autofmt_xdate()

plt.show()


#%%

# Load the new cruise data
atlantic = pd.read_csv("data/PLOTTING_processed_uws_data_with_uncertainty_bootstrapping.csv")
atlantic_subsamples = pd.read_csv("data/PLOTTING_subsamples_with_corrections.csv")

# Convert date columns to datetime if they're not already
atlantic['date_time'] = pd.to_datetime(atlantic['date_time'])
atlantic_subsamples['date_time'] = pd.to_datetime(atlantic_subsamples['date_time'])


# Set up the figure and gridspec
fig = plt.figure(figsize=(6, 10), dpi=300)
gs = gridspec.GridSpec(2, 1, height_ratios=[1, 1])

# === FIRST SUBPLOT
# === SIMPLE MOVING AVERAGE
# Compute simple moving average (SMA) over period of 30 minutes
atlantic["SMA"] = atlantic["pH_optode_corrected"].rolling(60, min_periods=1).mean()
atlantic["SMA_uncertainty"] = atlantic["pH_optode_corrected_RMSE"].rolling(60, min_periods=1).mean()

# Subplot for new Atlantic cruise (standard axis)
ax1 = fig.add_subplot(gs[0, 0])
L = atlantic["SMA"].notnull()
ax1.scatter(atlantic['date_time'][L], atlantic['pH_insitu_ta_est'][L], label='Uncorrected pH', s=0.1, color='xkcd:light pink', alpha=0.6)
ax1.scatter(atlantic['date_time'][L], atlantic['SMA'][L], label='Corrected pH', s=0.1, color='blue', alpha=0.6)

# Identify gaps in the data
gaps = atlantic['date_time'].diff() > pd.Timedelta(minutes=30)
gaps.iloc[0] = False  # First element cannot be a gap

# Split the data into continuous segments
segments = []
current_segment = []

for i, (is_gap, date, sma, sma_uncertainty) in enumerate(zip(gaps, atlantic['date_time'], atlantic['SMA'], atlantic['SMA_uncertainty'])):
    if is_gap and current_segment:
        segments.append(current_segment)
        current_segment = []
    current_segment.append((date, sma, sma_uncertainty))

if current_segment:
    segments.append(current_segment)

# Plot each segment separately
for segment in segments:
    dates, smas, sma_uncertainties = zip(*segment)
    dates = pd.to_datetime(dates)  # Ensure dates are in datetime format
    lower_bound = [sma - unc for sma, unc in zip(smas, sma_uncertainties)]
    upper_bound = [sma + unc for sma, unc in zip(smas, sma_uncertainties)]
    ax1.fill_between(dates, lower_bound, upper_bound, color='blue', alpha=0.2)

ax1.scatter(atlantic_subsamples["date_time"], atlantic_subsamples["pH_initial_talk_corr"], color='k', label='Subsamples $pH_{TA/DIC}$', s=20, alpha=0.6, edgecolor='k', zorder=6)

ax1.set_ylabel("$\mathrm{pH_{total}}$")

ax1.set_xlim(atlantic["date_time"].min(), atlantic["date_time"].max())
ax1.set_ylim(8.04, 8.20)

# Format the x-axis to show dates
ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

ax1.grid(True, alpha=0.3)

# Adjust the subplot to prevent overlap
plt.tight_layout(rect=[0, 0, 1, 0.95])

# Add label (a) to the first subplot
ax1.text(0, 1.08, 'a)', transform=ax1.transAxes, verticalalignment='top')

# === SECOND SUBPLOT
# Define start and end of the x-axis break for the original cruise
start_break = pd.Timestamp(2022, 3, 6)
end_break = pd.Timestamp(2022, 3, 24)

# Set the limits for the left side of the broken x-axis
L = (df["SMA"].notnull()) & (df["date_time"] > pd.Timestamp(2022, 3, 1, 15))
left_xlim = (df["date_time"][L].min(), start_break)

# Set the limits for the right side of the broken x-axis
right_xlim = (end_break, df["date_time"][L].max())

# Create broken axes plot with adjusted spacing and separate x-axis limits
bax = brokenaxes(xlims=(left_xlim, right_xlim), hspace=0.05, d=0, width_ratios=[1, 2], wspace=0.05, subplot_spec=gs[1, 0])

# Load GEOMAR pH data (SAMI)
geomar = pd.read_excel("data/SO289 carbonate data-Li Qiu-update_LD.xlsx")
geomar['datetime'] = pd.to_datetime(geomar['datetime'])
geomar["SMA"] = geomar["pH_meas"].rolling(60, min_periods=1).mean()
geomar["SMA_uncertainty"] = geomar["pH_meas_unc"].rolling(60, min_periods=1).mean()

geomar["SMA_pCO2"] = geomar["pH_calc_TA_pCO2_meas"].rolling(60, min_periods=1).mean()
# geomar["SMA_pCO21_uncertainty"] = geomar["pH_meas_unc"].rolling(60, min_periods=1).mean()

# Plot the data for the second subplot
L = df["SMA"].notnull()
bax.scatter(df["date_time"][L], df["pH_insitu_ta_est"][L], s=0.1, label="Uncorrected pH", color='xkcd:light pink', alpha=0.6)
bax.scatter(df["date_time"][L], df["SMA"][L], s=0.1, label="Corrected pH", color='b', alpha=0.6)
bax.fill_between(df["date_time"][L], df["SMA"][L] - df["SMA_uncertainty"][L], df["SMA"][L] + df["SMA_uncertainty"][L], color='b', alpha=0.2)

bax.scatter(geomar["datetime"], geomar["SMA"], s=0.1, label="Independent pH (SAMI)", color='k', alpha=0.6)
bax.fill_between(geomar["datetime"], geomar["SMA"] - geomar["SMA_uncertainty"], geomar["SMA"] + geomar["SMA_uncertainty"], color='k', alpha=0.2)
# bax.scatter(geomar["datetime"], geomar["SMA_pCO2"], s=0.1, label="Independent pH (SAMI)", color='k', alpha=0.6)

# Filter out subsamples that fall within the break period
mask = (subsamples_original["date_time"] < start_break) | (subsamples_original["date_time"] >= end_break)
filtered_subsamples = subsamples_original[mask]
bax.scatter(filtered_subsamples["date_time"], filtered_subsamples["pH_total_est_TA_DIC"], color='k', label='Subsamples $pH_{TA/DIC}$', s=20, alpha=0.6, edgecolor='k', zorder=6)

# Draw vertical lines at the break points
bax.axvline(start_break, color='k', linewidth=1.2)
bax.axvline(end_break, color='k', linewidth=1.2)

# Create right and top axis
bax2 = bax.twinx()[0]  # Get the first axes object from the list
bax3 = bax.twiny()[0]  # Get the first axes object from the list

bax2.set_ylabel('')
bax3.set_xlabel('')

bax2.set_yticks([])
bax3.set_xticks([])

bax2.set_yticklabels([])
bax3.set_xticklabels([])

# Now, loop through each subplot in your broken axis to adjust the labels
for i, ax in enumerate(bax.axs):
    # if i == 1:  # This is the top right axis
    #     # ax.xaxis.set_visible(False)
    # else:  # Rotate labels for the other x-axes
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

# Now, loop through each subplot in your broken axis to adjust the labels
for ax in bax.axs:
    labels = ax.get_xticklabels()
    new_labels = [label.get_text() if label.get_text() != '2022-03-24' else '' for label in labels]
    ax.set_xticklabels(new_labels)

# Add label (b) to the second subplot
bax.axs[0].text(0, 1.08, 'b)', transform=bax.axs[0].transAxes, verticalalignment='top')

# Add a legend
handles, labels = bax.get_legend_handles_labels()

custom_handles = [
    Line2D([0], [0], marker='o', color='w', label='Uncorrected pH', markersize=6, markerfacecolor='xkcd:light pink'),
    Line2D([0], [0], marker='o', color='w', label='Corrected pH', markersize=6, markerfacecolor='b'),
    Line2D([0], [0], marker='o', color='w', label='Subsamples $pH_{TA/DIC}$', markersize=6, markerfacecolor='k')
] + list(handles[2:])

legend = bax.legend(handles=custom_handles, loc="upper center", bbox_to_anchor=(0.5, -0.3), ncol=3, fontsize=8)

bax.set_ylabel("$\mathrm{pH_{total}}$")
bax.set_ylim(7.9, 8.15)
bax.grid(alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.95])

plt.savefig('figs/atlantic_pacific_corrections.png', dpi=300, bbox_inches='tight')

#%%
# Sort by datetime for merge_asof
# df = df.sort_values("date_time")
# geomar = geomar.sort_values("datetime")

# # Merge GEOMAR pH (SAMI) with closest South Pacific cruise pH
# matched = pd.merge_asof(
#     geomar[['datetime', 'SMA']],
#     df[['date_time', 'SMA']],
#     left_on='datetime',
#     right_on='date_time',
#     direction='nearest',
#     tolerance=pd.Timedelta(minutes=15)  # Max allowed time difference
# )

# # Drop unmatched rows
# matched = matched.dropna()

# from sklearn.metrics import mean_squared_error, r2_score
# import numpy as np

# # Calculate RMSD and R²
# rmsd = np.sqrt(mean_squared_error(matched['SMA_x'], matched['SMA_y']))
# r2 = r2_score(matched['SMA_x'], matched['SMA_y'])

# # Create figure and axis
# fig, ax = plt.subplots(figsize=(5, 5), dpi=300)

# # Scatter plot
# ax.scatter(matched['SMA_y'], matched['SMA_x'], s=10, alpha=0.5, color='k')

# # 1:1 line
# min_val = 7.96
# max_val = 8.08
# ax.plot([min_val, max_val], [min_val, max_val], 'k--', label='1:1 Line')

# # Labels and styling
# ax.set_xlabel("pH$_{optode}$")
# ax.set_ylabel("pH$_{SAMI}$")

# ax.grid(True, alpha=0.3)

# # Annotate RMSD and R²
# ax.text(0.02, 0.98,
#         f'RMSD = {rmsd:.4f}',
#         transform=ax.transAxes,
#         verticalalignment='top',
#         fontsize=10,
#         bbox=dict(facecolor='white', edgecolor='gray', boxstyle='round'))

# ax.set_xlim(7.96, 8.08)
# ax.set_ylim(7.96, 8.08)

# # Final layout and save
# fig.tight_layout()
# fig.savefig("figs/geomar_vs_south_pacific_with_rmsd_r2.png", dpi=300)
# plt.show()

#%%
# Sort by datetime for merge_asof
df = df.sort_values("date_time")
geomar = geomar.sort_values("datetime")

# Merge GEOMAR pH (SAMI) with closest South Pacific cruise pH (raw values)
matched = pd.merge_asof(
    geomar[['datetime', 'pH_meas', 'pH_meas_unc']],
    df[['date_time', 'pH_corrected', 'pH_uncertainty']],
    left_on='datetime',
    right_on='date_time',
    direction='nearest',
    tolerance=pd.Timedelta(minutes=1)  # Max allowed time difference
)

# Drop unmatched rows
matched = matched.dropna()

from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

# Calculate RMSD and R²
rmsd = np.sqrt(mean_squared_error(matched['pH_meas'], matched['pH_corrected']))
r2 = r2_score(matched['pH_meas'], matched['pH_corrected'])

# Create figure and axis
fig, ax = plt.subplots(figsize=(5, 5), dpi=300)

# Scatter plot
# ax.scatter(matched['pH_corrected'], matched['pH_meas'], s=10, alpha=0.5, color='k')

# Scatter plot with error bars
ax.errorbar(
    matched['pH_corrected'], matched['pH_meas'],
    xerr=matched['pH_uncertainty'], yerr=matched['pH_meas_unc'],
    fmt='o', markersize=3,
    elinewidth=0.5, capsize=1.5,
    alpha=0.5,
    markerfacecolor='none', markeredgecolor='k',
    ecolor='k'
)

# 1:1 line
min_val = 7.9
max_val = 8.2
ax.plot([min_val, max_val], [min_val, max_val], 'k--', label='1:1 Line')

# Labels and styling
ax.set_xlabel("pH$_{optode}$")
ax.set_ylabel("pH$_{SAMI}$")

ax.grid(True, alpha=0.3)

# Annotate RMSD
ax.text(0.02, 0.98,
        f'RMSD = {rmsd:.4f}',
        transform=ax.transAxes,
        verticalalignment='top',
        fontsize=10,
        bbox=dict(facecolor='white', edgecolor='gray', boxstyle='round'))

# Set limits
ax.set_xlim(7.9, 8.2)
ax.set_ylim(7.9, 8.2)

# Final layout and save
fig.tight_layout()
fig.savefig("figs/geomar_vs_south_pacific_raw.png", dpi=300)
plt.show()
