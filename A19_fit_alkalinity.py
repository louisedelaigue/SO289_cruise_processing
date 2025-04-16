import pandas as pd, numpy as np
from scipy.optimize import least_squares
from scipy import stats
from matplotlib import pyplot as plt

# Load discrete samples data
df = pd.read_csv("data/processing/vindta/SO289_underway_TA_DIC_only_results_with_uncertainty.csv")

# Drop outlier
L = df['alkalinity'] < 2000
df = df[~L]

# Drop where there's no DIC data
L = df['DIC'].isna()
df = df[~L]

# Define the function to estimate TA using Lee et al. (2006) equations
def ta_zone1(SSS, SST):
    """Estimate TA for cruise SO289"""
    return (
        2305
        + 58.66 * (SSS - 35)
        + 2.32 * (SSS - 35) ** 2
        - 1.41 * (SST - 20)
        + 0.040 * (SST - 20) ** 2
    )

# Apply the function to estimate TA and add it as a new column in the DataFrame
df['talk_lee'] = ta_zone1(df['SBE45_sal'], df['SBE38_water_temp'])

# Create to numpy arrays
sss = df["SBE45_sal"].to_numpy()
sst = df["SBE38_water_temp"].to_numpy()
alkalinity = df["alkalinity"].to_numpy()
dic = df["DIC"].to_numpy()

def get_alkalinity(coeffs, sss, sst, dic):
    a, b, c, d, e, f, g, h = coeffs
    return (
        a
        + b * (sss - 35)
        + c * ((sss - 35) ** 2)
        + d * (sst - 8)
        + e * ((sst - 8) ** 2)
        + f * dic / 1000
        + g * (dic / 1000) ** 2
        + h * (dic / 1000) ** 3
    )


def _lsqfun_get_alkalinity(coeffs, alkalinity, *args):
    return get_alkalinity(coeffs, *args) - alkalinity


opt_result = least_squares(
    _lsqfun_get_alkalinity,
    [2300, 2300 / 35, 0, 0, 0, 0, 0, 0],
    args=(alkalinity, sss, sst, dic),
)


coeffs = opt_result["x"]
alkalinity_pred = get_alkalinity(opt_result["x"], sss, sst, dic)

# Root-mean-square error / use as 1-sigma uncertainty
rmse = np.sqrt(np.mean((alkalinity_pred - alkalinity) ** 2))

# Add predicted alkalinity back to df (df)
df["talk_fit"] = alkalinity_pred

# Uncertainty propagation salinity, temperature and dic
# Below come from https://statics.teams.cdn.office.net/evergreen-assets/safelinks/1/atp-safelinks.html
temperature_uncertainty = 0.002
salinity_uncertainty = 0.01
dic_uncertainty = 2.4

alkalinity_pred_temp = (
    get_alkalinity(coeffs, sss, sst + temperature_uncertainty, dic) - df["talk_fit"]
).max()
alkalinity_pred_salinity = (
    get_alkalinity(coeffs, sss + salinity_uncertainty, sst, dic) - df["talk_fit"]
).max()
alkalinity_pred_dic = (
    get_alkalinity(coeffs, sss, sst, dic + dic_uncertainty) - df["talk_fit"]
).max()

# ^^^ these are negligible compared to RMSE = 5.44
# And if you do np.sqrt(0.5**2 + 5.44**2) to add the salinity uncertainty, still less
# than 5.5 so could argue we are already including all uncertainty using RMSE = 5.5

# === Plot to compare df obs vs. fit
# Create plot
fig, ax = plt.subplots(dpi=300, figsize=(6, 4))

# Scatter data
plot = ax.scatter(
    "alkalinity",
    "talk_fit",
    data=df,
    s=10,
    alpha=0.3,
    edgecolor="none",
    zorder=1,
)

# Plot 1:1 line
ax.axline([2300, 2300], slope=1, c="black", alpha=0.7, zorder=0)

# Add R2 to plot
R2 = round((stats.linregress(df["talk_fit"], df["alkalinity"])[2]) ** 2, 3)
ax.text(2265, 2385, "$R^{}$ = {}".format("2", R2))

# Scale figure and remove outlier
# ^^^ mention this in the figure caption
ax.set_xlim(2260, 2400)
ax.set_ylim(2260, 2400)
ax.set_xticks(np.linspace(2260, 2400, 8))
ax.set_yticks(np.linspace(2260, 2400, 8))

# Improve figure
ax.grid(alpha=0.3)
ax.set_xlabel("$A_{T}$ $_{fitted}$ / μmol · $kg^{-1}$")
ax.set_ylabel("$A_{T}$ $_{dfv2.2022}$ / μmol · $kg^{-1}$")

# Save figure
plt.tight_layout()
# plt.savefig("./figs/paper/alkalinity_df_fit_withtemp.png", dpi=300)
#%%
# === Plot to compare obs. vs Lee fit
# Create plot
fig, ax = plt.subplots(dpi=300, figsize=(6, 4))

# Add data
ax.scatter(
    "dic",
    "talk",
    data=df,
    s=10,
    marker="o",
    alpha=0.3,
    color="xkcd:blue",
    edgecolor="none",
    label="$A_{T}$ $_{dfv2.2022}$",
)

L = df["dic"] <= 50
ax.scatter(
    "dic",
    "talk_lee",
    data=df[L],
    s=10,
    marker="s",
    alpha=0.3,
    color="xkcd:tangerine",
    edgecolor="none",
    label="$A_{T}$ $_{Lee}$ $_{et}$ $_{al.}$$_{(2006)}$$_{-}$$_{surface}$",
)

L = df["dic"] > 50
ax.scatter(
    "dic",
    "talk_lee",
    data=df[L],
    s=10,
    marker="^",
    alpha=0.3,
    color="xkcd:black",
    edgecolor="none",
    label="$A_{T}$ $_{Lee}$ $_{et}$ $_{al.}$$_{(2006)}$$_{-}$$_{deep}$",
)

ax.invert_yaxis()

# Scale figure and remove outlier
# ^^^ mention this in the figure caption
# Only down to 2000 m because we are only interested in the fit for the df here
ax.set_xlim(0, 2000)
ax.set_ylim(2260, 2400)
ax.set_xticks(np.linspace(0, 2000, 9))
ax.set_yticks(np.linspace(2260, 2400, 8))

# Improve figure
ax.grid(alpha=0.3)
ax.set_xlabel("dic / m")
ax.set_ylabel("$A_{T}$ / μmol · $kg^{-1}$")
ax.legend(markerscale=1.5, fontsize=10)

# Save figure
plt.tight_layout()
# plt.savefig("./figs/paper/alkalinity_df_lee_dic.png", dpi=300)

# === Plot fit vs. dic
# Create plot
fig, ax = plt.subplots(dpi=300, figsize=(6, 4))

# Add data
ax.scatter(
    "dic",
    "talk",
    data=df,
    s=10,
    marker="o",
    alpha=0.3,
    color="xkcd:blue",
    edgecolor="none",
    label="$A_{T}$ $_{dfv2.2022}$",
    zorder=0,
)

ax.scatter(
    "dic",
    "talk_fit",
    data=df,
    s=10,
    marker="^",
    alpha=0.3,
    color="xkcd:tangerine",
    edgecolor="none",
    label="$A_{T}$ $_{fitted}$",
    zorder=1,
)

ax.invert_yaxis()

# Scale figure and remove outlier
# ^^^ mention this in the figure caption
# Only down to 2000 m because we are only interested in the fit for the df here
ax.set_xlim(0, 2000)
ax.set_ylim(2260, 2400)
ax.set_xticks(np.linspace(0, 2000, 9))
ax.set_yticks(np.linspace(2260, 2400, 8))

# Improve figure
ax.grid(alpha=0.3)
ax.set_xlabel("dic / m")
ax.set_ylabel("$A_{T}$ / μmol · $kg^{-1}$")
ax.legend(markerscale=1.5, fontsize=10)

# Save figure
plt.tight_layout()
plt.savefig("./figs/paper/alkalinity_df_fit_dic.png", dpi=300)