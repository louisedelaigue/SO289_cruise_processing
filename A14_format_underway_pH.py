import pandas as pd
from datetime import datetime

# Load underway pH data
df = pd.read_csv("data/processing/optode/A10_uws_correct_pH.csv")

# Create EXPOCODE and Cruise ID column
df["EXPOCODE"] = "06S220220218"
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

# Add a flag column for pH
df["pH_flag"] = 2

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
    "pH_TS_measured (optode)",
    "pH_flag"
    ]]

# Drop rows with no pH
df = df.dropna(subset="pH_TS_measured (optode)")

# Fill missing values if any
df = df.fillna(-999)

# Reset index
df = df.reset_index()

# Drop useless columns
df = df.drop(columns="index")

# Add row for units
units = {
    "EXPOCODE":"n.a.",
    "Cruise_ID":"n.a",
    "Year_UTC":"n.a.",
    "Month_UTC":"n.a.",
    "Day_UTC":"n.a.",
    "Time_UTC":"n.a.",
    "Latitude":"decimal_deg",
    "Longitude":"decimal_deg",
    "Depth":"[m]",
    "Temperature":"[deg_C]",
    "TEMP_pH":"[deg_C",
    "Salinity":"n.a.",
    "pH_TS_measured (optode)":"n.a.",
    "pH_flag":"n.a."
}

# Store the current column names
# If columns are multi-index, get the first level. Otherwise, get the column name.
current_columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

# Add units as a new row at the top
df.loc[-1] = [units.get(col, 'n.a.') for col in current_columns]
df.index = df.index + 1  # Shift index
df = df.sort_index()  # Sort by index to get the new row on top

# Reset column headers
df.columns = current_columns

# Add information lines
info_lines = [
    "# File last updated on: {}".format(datetime.today().strftime('%d %B %Y')),														
    "# File prepared by: Louise Delaigue (Royal Netherlands Institute for Sea Research)", 														
    "# For questions please send a message to:  louise.delaigue@nioz.nl or matthew.humphreys@nioz.nl",														
    "# EXPOCODE: 06S220220218",														
    "# Chief Scientist: Prof. Dr. Eric P. Achterberg (GEOMAR)",														
    "# Region: South Pacific Ocean (GEOTRACES GP21)",													
    "# SHIP: R/V Sonne",														
    "# Cruise:  SO289",														
    "# Shipboard contact: sonne@sonne.briese-research.de",														
    "# Notes: code for processing SO289 data can be found at https://zenodo.org/badge/latestdoi/563245618",																											
    "# pH: Who - L.Delaigue; Status - Final",														
    "# Notes: measured using a PyroScience fiber-based pH sensor (PHROBSC-PK8T for pH range 7.0 to 9.0 on total scale) recalculated at in-situ temperature and pressure and corrected using TA/DIC from underway discrete samples",																									
    "#  "
]

filename = "data/_results/SO289_UWS_time_series_V1.csv"

# Write the info lines
with open(filename, 'w') as f:
    for line in info_lines:
        f.write(line + '\n')

# Append the dataframe
df.to_csv(filename, mode='a', index=False)