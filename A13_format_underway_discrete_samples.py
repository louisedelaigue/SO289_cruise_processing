import pandas as pd
import re

# Load discrete samples data
df = pd.read_csv("data/_results/SO289_underway_TA_DIC_only_results.csv")

# Convert to datetime object
df["date_time"] = pd.to_datetime(df["date_time"])

# Add date and time
df["Year_UTC"] = df["date_time"].dt.year
df["Month_UTC"] = df["date_time"].dt.month
df["Day_UTC"] = df["date_time"].dt.day
df["Time_UTC"] = df["date_time"].dt.time

# Add depth column
df["Depth"] = 3

# Convert latitude and longitude
df["lat"] = df["lat"].apply(lambda x: "".join(filter(None, x.split(" "))))
df["lon"] = df["lon"].apply(lambda x: "".join(filter(None, x.split(" "))))


def dms_to_dd(lat_or_lon):
    """Convert coordinates from degrees to decimals."""
    deg, minutes, seconds, direction = re.split("[°\.'\"]", lat_or_lon)
    ans = ((float(deg) + float(minutes) / 60) + float(seconds) / (60 * 60)) * (
        -1 if direction in ["W", "S"] else 1
    )
    return pd.Series({"decimals": ans})


# convert lat/lon to decimals
df["lat"] = df.lat.apply(dms_to_dd)
df["lon"] = df.lon.apply(dms_to_dd)

# Rename columns
rn = {
    "SBE45_sal": "Salinity",
    "SBE38_water_temp": "Temperature",
    "alkalinity": "TA",
    "lat": "Latitude",
    "lon": "Longitude",
}
df = df.rename(columns=rn)

# Add missing columns
df["EXPOCODE"] = "TBD"
df["Cruise_ID"] = "SO289"

# Keep and order columns
df = df[
    [
        "EXPOCODE",
        "Year_UTC",
        "Month_UTC",
        "Day_UTC",
        "Time_UTC",
        "Latitude",
        "Longitude",
        "Depth",
        "Temperature",
        "Salinity",
        "TA",
        "DIC",
    ]
]

# Fill missing values
df = df.fillna(-999)

# Save as .csv
df.to_csv("data/_results/SO289_underway_TA_DIC.csv", index=False)
