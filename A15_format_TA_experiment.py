import pandas as pd
import calkulate as calk
from datetime import datetime

# === ALKALINITY SAMPLES
# Import TA only data post-R2CO2 processing for TA experiment
TALK = pd.read_csv("data/processing/vindta/SO289_TA_exp_TA_only_results.csv")

# Drop suffix
TALK['bottle'] = TALK['bottle'].str.replace('AE-', '', regex=True)

# Turn all letters to uppercase
TALK['bottle'] = TALK['bottle'].str.upper()

# Assign metadata for alkalinity experiment samples
meta = pd.read_excel("data/vindta/TA_ONLY/SO289_NaOH.xlsx", na_values="<LOD")

# Create an experiment number column
TALK['exp_number'] = TALK['bottle'].str.extract('(\d+)').astype(int)

# Create a list of experiments
experiments = list(meta["Exp."].unique())

for e in experiments:
    TALK.loc[TALK["exp_number"] == e, "Sample_date"] = meta.loc[
        meta["Exp."] == e, "Date"
    ].item()
    TALK.loc[TALK["exp_number"] == e, "Sample_time"] = meta.loc[meta["Exp."] == e, "Time"].item()
    TALK.loc[TALK["exp_number"] == e, "Latitude"] = meta.loc[
        meta["Exp."] == e, "Lat"
    ].item()
    TALK.loc[TALK["exp_number"] == e, "Longitude"] = meta.loc[
        meta["Exp."] == e, "Lon"
    ].item()
    TALK.loc[TALK["exp_number"] == e, "Initial_temperature"] = meta.loc[
        meta["Exp."] == e, "SST"
    ].item()

# Convert to datetime format for date and time separately
TALK['date'] = pd.to_datetime(TALK['Sample_date'], format='%d/%m/%Y')
TALK['time_obj'] = pd.to_datetime(TALK['Sample_time'], format='%H:%M:%S').dt.time

# Extract year, month, day
TALK['Year_UTC'] = TALK['date'].dt.year
TALK['Month_UTC'] = TALK['date'].dt.month
TALK['Day_UTC'] = TALK['date'].dt.day
TALK['Time_UTC'] = TALK['time_obj']

# Drop the intermediate date and time_obj columns
TALK = TALK.drop(columns=['date', 'time_obj', "Sample_date", "Sample_time"])
      
# === DIC SAMPLES
DIC = pd.read_excel("data/quaatro/DIC_vials/TA_experiment_DIC_friendly.xlsx")

# === MERGED DF
# Identifying unmatched rows
df = pd.merge(TALK, DIC, left_on='bottle', right_on='Sample', how='outer', indicator=True)

unmatched_TALK = df[df['_merge'] == 'left_only']
unmatched_DIC = df[df['_merge'] == 'right_only']

print("Unmatched from TALK:")
print(unmatched_TALK)

print("\nUnmatched from DIC:")
print(unmatched_DIC)

# Rename _merge column tags
df['_merge'] = df['_merge'].replace({'left_only': 'TA only', 'right_only': 'DIC only'})

# Calculate density of each sample at lab temperature (= 20 deg C in raw KB files) and sample salinity
df['density'] = calk.density.seawater_1atm_MP81(20, df['salinity'])

# Convert from umol/L to umol/kg for DIC only (K. Bakker lab analysis)
df['DIC'] = df['DIC'] / df['density']

# Drop density column
df = df.drop(columns=["density"])

# Add flag column for TA
df["TA_flag"] = 2

# Add EXPOCODE and Cruise_ID columns
df["EXPOCODE"] = "06S220220218"
df["Cruise_ID"] = "SO289"

# Rename columns
rn = {
      "bottle":"TA_bottle_name",
      "Sample":"DIC_vial_name",
      "_merge":"availability",
      "Flag":"DIC_flag",
      "alkalinity":"TA",
      "salinity":"Initial_salinity",
      "total_phosphate":"Initial_total_phosphate",
      "total_silicate":"Initial_total_silicate",   
      }

df.rename(columns=rn, inplace=True)

# Reorder df
df = df[[
    "EXPOCODE",
    "Cruise_ID",
    "TA_bottle_name",
    "DIC_vial_name",
    "Year_UTC",
    "Month_UTC",
    "Day_UTC",
    "Time_UTC",
    "Initial_salinity",
    "Initial_temperature",
    "Initial_total_phosphate",
    "Initial_total_silicate",
    "TA",
    "TA_flag",
    "DIC",
    "DIC_flag",
    "availability",
    "Notes"
    ]]

# Add row for units
units = {
    "EXPOCODE":"n.a.",
    "Cruise_ID":"n.a.",
    "TA_bottle_name":"n.a.",
    "DIC_vial_name":"n.a.",
    "Year_UTC":"n.a.",
    "Month_UTC":"n.a.",
    "Day_UTC":"n.a.",
    "Time_UTC":"n.a.",
    "Initial_salinity":"n.a.",
    "Initial_total_phosphate":"[umol/kg]",
    "Initial_total_silicate":"[umol/kg]",
    "TA":"[umol/kg]",
    "TA_flag":"n.a.",
    "DIC":"[umol/kg]",
    "DIC_flag":"n.a.",
    "availability":"n.a.",
    "Notes":"n.a.",
}

# Store the current column names
# If columns are multi-index, get the first level. Otherwise, get the column name.
current_columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

# Add units as a new row at the top
df.loc[-1] = [units.get(col, 'n.a.') for col in current_columns]
df.index = df.index + 1  # Shift index
df = df.sort_index()  # Sort by index to get the new row on top

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
    "# Notes: code for processing SO289 data can be found at doi",																											
	"# DIC: Who - K. Bakker; Status -  Final",																												
    "# Notes:  analysed at the Royal Netherlands Institute for Sea Resarch using a Seal QuAAtro gas-segmented continuous flow analyser and Dickson's CRMs (batch #195)",																												
    "# TA: Who - L. Delaigue; Status -  Final	",																											
    "# Notes:  analysed at the Royal Netherlands Institute for Sea Resarch using a VINDTA 3C (#017 Marianda Germany) and Dickson's CRMs (batch #189 #195 #198)",						
    "# Notes: TA and DIC were sampled separatly in 150 mL HDPE plastic bottles and 12 mL exetainer vials respectively",
    "#  "
]

filename = "data/_results/SO289_TA_enhancement_experiment_V1.csv"

# Write the info lines
with open(filename, 'w') as f:
    for line in info_lines:
        f.write(line + '\n')

# Append the dataframe
df.to_csv(filename, mode='a', index=False)