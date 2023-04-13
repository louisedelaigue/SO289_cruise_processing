import pandas as pd, seaborn as sns
import matplotlib.pyplot as plt

# Import data
df = pd.read_csv("data/processing/optode/A10_uws_correct_pH_subsamples.csv")

# ===== PLOTS
# === LINEAR REGRESSION
# Prepare figure
sns.set_style("darkgrid")
sns.set_context("paper", font_scale=1)
sns.set(font="Verdana", font_scale=1)

# Create figure
fig, ax = plt.subplots(dpi=300, figsize=(7, 6))

# Linear regression
sns.regplot(
    y="pH_total_est_TA_DIC",
    x="pH_optode",
    data=df,
    color="xkcd:blue",
    label="South Pacific",
    ax=ax,
)


# Add R2 to plot
# ax.text(2102, 2172, "$R^2$(O) = {}".format(R2_orig), fontsize=15)
# ax.text(2102, 2162, "$R^2$(R) = {}".format(R2_recalc), fontsize=15)

# Improve figure
ymin = 7.9
ymax = 8.15
xmin = 7.9
xmax = 8.15
plt.xlim([xmin, xmax])
plt.ylim([ymin, ymax])

# Line through origin
x = [xmin, xmax]
y = [ymin, ymax]
x_values = [x[0], x[1]]
y_values = [y[0], y[1]]
sns.lineplot(
    x=x_values,
    y=y_values,
    ax=ax,
    linestyle="--",
    color="black",
    label="Perfect fit",
    zorder=0
)



ax.set_ylabel("$pH_{total}$ calc(TA/DIC)")
ax.set_xlabel("$pH_{total}$ optode")

# Save plot
plt.savefig("./figs/P04_plot_raw_optode_vs_corrected_subsamples.png")
