import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# from sklearn.metrics import r2_score

# === SO279
# Load discrete samples data
atlantic = pd.read_csv("C:/Users/ldelaigue/Documents/GitHub/SO279_cruise_processing/data/SO279_UWS_discrete_samples.csv", na_values=-999)

# Define the function to estimate TA using Lee et al. (2006) equations
def ta_north_atlantic(SSS, SST):
    """Estimate TA for North Atlantic region."""
    return (
        2305
        + 53.97 * (SSS - 35)
        + 2.74 * (SSS - 35) ** 2
        - 1.16 * (SST - 20)
        - 0.040 * (SST - 20) ** 2
    )

# Apply the function to estimate TA and add it as a new column in the DataFrame
atlantic['ta_est'] = ta_north_atlantic(atlantic['Salinity'], atlantic['Temperature'])

# Calculate residuals
atlantic['residuals'] = atlantic['TA'] - atlantic['ta_est']

# === SO289
# Load discrete samples data
pacific = pd.read_csv("data/processing/vindta/SO289_underway_TA_DIC_only_results_with_uncertainty.csv")

# Drop outlier
L = pacific['alkalinity'] < 2030
pacific = pacific[~L]

# Define the function to estimate TA using Lee et al. (2006) equations
def ta_subtropics(SSS, SST):
    """Estimate TA for (Sub)tropics region."""
    return (
        2305
        + 58.66 * (SSS - 35)
        + 2.32 * (SSS - 35) ** 2
        - 1.41 * (SST - 20)
        + 0.040 * (SST - 20) ** 2
    )

# Apply the function to estimate TA and add it as a new column in the DataFrame
pacific['ta_est'] = ta_subtropics(pacific['SBE45_sal'], pacific['SBE38_water_temp'])

# Calculate residuals
pacific['residuals'] = pacific['alkalinity'] - pacific['ta_est']

# === PLOT
# Create a figure
fig, (ax1, ax2) = plt.subplots(1, 2, dpi=300, figsize=(9, 4))

# First subplot for Atlantic
plot1 = ax1.scatter(
    atlantic['TA'],
    atlantic['ta_est'],
    s=10,
    c='xkcd:royal purple',
    alpha=0.6,
    edgecolor="none",
    zorder=1,
)

# Plot 1:1 line for Atlantic
ax1.plot([2300, 2500], [2300, 2500], 'k--', alpha=0.7, zorder=0)

# Scale and labels for Atlantic subplot
ax1.set_xlim(2300, 2500)
ax1.set_ylim(2300, 2500)
ax1.set_xticks(np.linspace(2300, 2500, 5))
ax1.set_yticks(np.linspace(2300, 2500, 5))
ax1.grid(alpha=0.3)
ax1.set_xlabel("TA $_{NA\ (Lee\ et\ al.\ 2006)}$ (μmol · kg$^{-1}$)")
ax1.set_ylabel("TA $_{measured}$ (μmol · kg$^{-1}$)")

# Add label "b)"
ax1.text(0, 1.08, 'a)', transform=ax1.transAxes, va='top', ha='left')

# Optional R^2 calculation and annotation for Atlantic
# R2_atlantic = r2_score(atlantic['TA'], atlantic['ta_est'])
# ax2.text(2305, 2485, f"$R^2$ = {R2_atlantic:.3f}")

# Second subplot for Pacific
plot2 = ax2.scatter(
    pacific['alkalinity'],
    pacific['ta_est'],
    s=10,
    c='xkcd:royal purple',
    alpha=0.6,
    edgecolor="none",
    zorder=1,
)

# Plot 1:1 line for Pacific
ax2.plot([2250, 2350], [2250, 2350], 'k--', alpha=0.7, zorder=0)

# Scale and labels for Pacific subplot
ax2.set_xlim(2250, 2350)
ax2.set_ylim(2250, 2350)
ax2.set_xticks(np.linspace(2250, 2350, 5))
ax2.set_yticks(np.linspace(2250, 2350, 5))
ax2.grid(alpha=0.3)
ax2.set_xlabel("TA $_{SBT\ (Lee\ et\ al.\ 2006)}$ (μmol · kg$^{-1}$)")
ax2.set_ylabel("TA $_{measured}$ (μmol · kg$^{-1}$)")

# Add label "a)"
ax2.text(0, 1.08, 'b)', transform=ax2.transAxes, va='top', ha='left')

# Optional R^2 calculation and annotation for Pacific
# R2_pacific = r2_score(pacific['alkalinity'], pacific['ta_est'])
# ax2.text(2252, 2343, f"$R^2$ = {R2_pacific:.3f}")

# Improve overall layout and show the plot
plt.tight_layout()

plt.savefig("./figs/alkalinity_lee_fit_SO279_SO289.png", dpi=300)
plt.show()
