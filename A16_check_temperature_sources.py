# This script plots all temperatures sources, from the PyroScience pt-100 sensor
# and the SMB 


import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

# Import UWS continuous pH data
df = pd.read_csv("./data/processing/optode/A10_uws_correct_pH.csv")

# Ensure datetime parsing
df['date_time'] = pd.to_datetime(df['date_time'])

# Create list of columns
columns = list(df.columns)

# Create figure
fig, ax = plt.subplots(dpi=300, figsize=(6, 4))

# Plot raw pH data
ax.scatter(
    df["date_time"],
    df["temp_cell"],
    label="pt-100 sensor",
    color="blue",
    s=1,
    alpha=0.6,
)

# Plot corrected pH data
ax.scatter(
    df["date_time"],
    df["SBE38_water_temp"],
    label="In-situ temperature",
    color="black",
    s=1,
    alpha=0.4,
)


ax.set_title(
    "Comparison of pt-100 temperature sensor and in-situ temperature", fontsize=10
)
ax.set_ylabel("Temperature (°C)")
ax.set_xlabel("Date")
# ax.set_ylim(19.5, 20.5)
ax.xaxis.set_major_locator(mdates.AutoDateLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
ax.tick_params(axis="both", which="major")
fig.autofmt_xdate()
ax.grid(alpha=0.3)

start_date = mdates.date2num(datetime.datetime.strptime("2022-02-22", "%Y-%m-%d"))
end_date = mdates.date2num(datetime.datetime.strptime("2022-04-06", "%Y-%m-%d"))

# Set the x-axis limits
ax.set_xlim(start_date, end_date)

# Add legend
ax.legend(loc="best", fontsize=10, markerscale=5)