import pandas as pd
import calkulate as calk
from datetime import datetime

# Load CTD data
df = pd.read_csv("data/processing/SO289_CTD_data_TA_DIC_combined.csv")

# Remove rows with no CTD info
df = df.dropna(how="any", subset=["station"])

# Only keep rows with TA/DIC data
df = df.dropna(how="all", subset=["alkalinity", "dic_corrected", "TA_only", "DIC_only"])

# Calculate density of each sample at lab temperature (= 23 deg C) and sample salinity
df["density"] = calk.density.seawater_1atm_MP81(23, df["salinity"])

# Convert from umol/L to umol/kg for DIC only (K. Bakker lab analysis)
df["DIC_only"] = df["DIC_only"] / df["density"]

# Remove "SO289" from station and create a cast column
df["station"] = df["station"].astype(str)
df["station"] = [s.replace("SO289_", "") for s in df["station"]]
df["Cast_number"] = [c.split("-")[1] for c in df["station"]]
df["station"] = [s.split("-")[0] for s in df["station"]]
df["station"] = [str(s).zfill(2) if len(s)<2 else str(s) for s in df["station"]]

# Add time column
df["hour"] = [str(h).replace(".0", "") for h in df["hour"]]
df["minute"] = [str(m).replace(".0", "") for m in df["minute"]]
df["second"] = [str(s).replace(".0", "") for s in df["second"]]

# Add leading zero if only one number in time column
df["hour"] = [str(h).zfill(2) if len(h)<2 else str(h) for h in df["hour"]]
df["minute"] = [str(m).zfill(2) if len(m)<2 else str(m) for m in df["minute"]]
df["second"] = [str(s).zfill(2) if len(s)<2 else str(s) for s in df["second"]]

df["time"] = df["hour"] + ":" + df["minute"] + ":" + df["second"]

# Add flag columns for TA and DIC
df["TA_flag"] = 2
df["DIC_flag"] = 2
df["TA_ONLY_flag"] = 2
df["DIC_ONLY_flag"] = 2

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
      "alkalinity":"TA",
      "dic_corrected":"DIC",
      "TA_only":"TA_ONLY",
      "DIC_only":"DIC_ONLY"
      }

df = df.rename(columns=rn)

# Add missing columns
df["EXPOCODE"] = "06S220220218"
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
    "TA",
    "TA_flag",
    "TA_ONLY",
    "TA_ONLY_flag",
    "DIC",
    "DIC_flag",
    "DIC_ONLY",
    "DIC_ONLY_flag"
    ]]

# Fill missing values
df = df.fillna(-999)

# Add row for units
units = {
    "EXPOCODE":"n.a.",
    "Cruise_ID":"n.a",
    "Station_ID":"n.a.",
    "Niskin_ID":"n.a.",
    "Year_UTC":"n.a.",
    "Month_UTC":"n.a.",
    "Day_UTC":"n.a.",
    "Time_UTC":"n.a.",
    "Latitude":"decimal_deg",
    "Longitude":"decimal_deg",
    "CTDPRES":"[bars]",
    "Depth":"[m]",
    "CTDTEMP_ITS90":"[deg_C]",
    "CTDSAL_PSS78":"n.a.",
    "TA":"[umol/kg]",
    "TA_flag":"n.a.",
    "TA_ONLY":"[umol/kg]",
    "TA_ONLY_flag":"n.a.",
    "DIC":"[umol/kg]",
    "DIC_flag":"n.a.",
    "DIC_ONLY":"[umol/kg",
    "DIC_ONLY_flag":"n.a."
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
    "# Chief Scientist: Dr. Eric P. Achterberg (GEOMAR)",														
    "# Region: South Pacific Ocean (GEOTRACES GP21)",													
    "# SHIP: R/V Sonne",														
    "# Cruise:  SO289",														
    "# Shipboard contact: sonne@sonne.briese-research.de",														
    "# Notes: code for processing SO289 data can be found at doi",																											
	"# DIC: Who - L. Delaigue; Status -  Final",																												
    "# Notes:  analysed at the Royal Netherlands Institute for Sea Resarch using a VINDTA 3C (#017 Marianda Germany) and Dickson's CRMs (batches #189 #195 #198)",																												
    "# TA: Who - L. Delaigue; Status -  Final	",																											
    "# Notes:  analysed at the Royal Netherlands Institute for Sea Resarch using a VINDTA 3C (#017 Marianda Germany) and Dickson's CRMs (batch #189 #195 #198)",						
    "# Notes: TA and DIC were both measured at the same time from 250 mL borosilicate glass bottles",
    "# Notes: TA_ONLY and DIC_ONLY were sampled and measured separatly from 150 mL HDPE plastic bottles on a VINDTA 3C and 12 mL exetainer vials respectively on a Seal QuAAtro gas-segmented continuous flow analyser",
    "#  "
]

filename = "data/_results/SO289_CTD_discrete_samples_V1.csv"

# Write the info lines
with open(filename, 'w') as f:
    for line in info_lines:
        f.write(line + '\n')

# Append the dataframe
df.to_csv(filename, mode='a', index=False)