import pandas as pd
import re

# Load underway pH data
df = pd.read_csv("data/processing/optode/A10_uws_correct_pH.csv")

# Create EXPOCODE and Cruise ID column
df["EXPOCODE"] = "TBD"
df["Cruise_ID"] = "SO289"

# Convert to datetime object
df["date_time"] = pd.to_datetime(df["date_time"])

# Add date and time
df["Year_UTC"] = df["date_time"].dt.year
df["Month_UTC"] = df["date_time"].dt.month
df["Day_UTC"] = df["date_time"].dt.day
df["Time_UTC"] = df["date_time"].dt.time

# Add depth column
df["Depth"] = 3

# Add second temperature column
df["TEMP_pH"] = df["SBE38_water_temp"]

# Rename columns
rn = {
    "lat": "Latitude",
    "lon": "Longitude",
    "SBE38_water_temp":"Temperature",
    "SBE45_sal":"Salinity",
    "pH_optode_corrected":"pH_TS_measured (optode)"
}
df = df.rename(columns=rn)

# Reorder columns
df = df[[
    "EXPOCODE",
    "Cruise_ID",
    "Year_UTC",
    "Month_UTC",
    "Day_UTC",
    "Time_UTC",
    "Latitude",
    "Longitude",
    "Depth",
    "Temperature",
    "TEMP_pH",
    "Salinity",
    "pH_TS_measured (optode)"
    ]]

# Drop rows with no pH
df = df.dropna(subset="pH_TS_measured (optode)")

# Fill missing values if any
df = df.fillna(-999)