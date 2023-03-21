import pandas as pd, numpy as np

# Load CTD data
df = pd.read_csv('data/SO289_CTD_data_TA_DIC.csv')

# Remove rows with no CTD info
df = df.dropna(how="any", subset=["station"])

# Only keep rows with TA/DIC data
df = df.dropna(how='all', subset=['alkalinity', 'dic_corrected', 'TA_only', 'DIC_only'])

# Remove "SO289" from station and create a cast column
df["station"] = df["station"].astype(str)
df["station"] = [s.replace("SO289_", "") for s in df["station"]]
df["Cast_number"] = [c.split("-")[1] for c in df["station"]]
df["station"] = [s.split("-")[0] for s in df["station"]]

# Add time column
df["hour"] = [str(h).replace(".0", "") for h in df["hour"]]
df["minute"] = [str(m).replace(".0", "") for m in df["minute"]]
df["second"] = [str(s).replace(".0", "") for s in df["second"]]

# Add leading zero if only one number in time column
df["hour"] = [str(h).zfill(2) if len(h)<2 else str(h) for h in df["hour"]]
df["minute"] = [str(m).zfill(2) if len(m)<2 else str(m) for m in df["minute"]]
df["second"] = [str(s).zfill(2) if len(s)<2 else str(s) for s in df["second"]]

df["time"] = df["hour"] + ":" + df["minute"] + ":" + df["second"]

# Rename columns
rn = {
      "station":"Station_ID",
      "niskin":"Niskin_ID",
      "year":"Year_UTC",
      "month":"Month_UTC",
      "day":"Day_UTC",
      "time":"Time_UTC",
      "latitude":"Latitude",
      "longitude":"Longitude",
      "pressure":"CTDPRES",
      "depth":"Depth",
      "temperature":"CTDTEMP_ITS90",
      "salinity":"CTDSAL_PSS78",
      }

df = df.rename(columns=rn)

# Add missing columns
df["EXPOCODE"] = np.nan
df["Cruise_ID"] = "SO289"

# Keep and order columns
df = df[[
    "EXPOCODE",
    "Cruise_ID",
    "Station_ID",
    "Niskin_ID",
    "Year_UTC",
    "Month_UTC",
    "Day_UTC",
    "Time_UTC",
    "Latitude",
    "Longitude",
    "CTDPRES",
    "Depth",
    "CTDTEMP_ITS90",
    "CTDSAL_PSS78",
    "alkalinity",
    "TA_only",
    "dic_corrected",
    "DIC_only"
    ]]

# Save as .csv
df.to_csv('data/SO289_CTD_data_final_temp.csv', index=False)