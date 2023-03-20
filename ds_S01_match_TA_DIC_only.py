import pandas as pd, numpy as np

# === ALKALINITY SAMPLES
# Import CTD data post-R2CO2 processing
TALK = pd.read_csv("data/SO289-TA_only_results.csv")

# Only keep data for SO290
L = TALK["bottle"].str.startswith("SO289")
TALK = TALK[L]

# Only keep UWS sub
TALK = TALK[TALK["bottle"].astype(str).map(len)>11]

# Only keep relevant columns
TALK = TALK[[
    "bottle",
    "salinity",
    "alkalinity", 
    ]]

# Reimport datetime column
TALK_meta = pd.read_csv("data/processing/uws_S06_match_samples_SMB_sal_temp.csv")

# Merge columns
df = TALK.merge(TALK_meta, on="bottle", how="inner")

# Drop "SO289" prefix for bottle names
TALK["bottle"] = TALK["bottle"].str.replace("SO289-", "")

# === DIC SAMPLES
DIC = pd.read_excel("data/raw_files/DIC_vials/230112 DIC LOUISE DR1R1_format_friendly.xlsx")

# Only keep good data
L = DIC["Flag"]==2
DIC = DIC[L]

# Remove white space
# DIC = DIC.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# Convert to datetime
DIC["date_time"] = pd.to_datetime(DIC["date_time"], format="%d/%m/%y %H:%M")
df["date_time"] = pd.to_datetime(df["date_time"])

# Add DIC back to df
df = df.merge(DIC, on="date_time", how="inner")

# === CLEAN UP FINAL DF
df = df[[
    "date_time",
    "SBE45_sal",
    "SBE38_water_temp",
    "alkalinity",
    "DIC"
    ]]

# Save to .csv
df.to_csv("data/processing/ds_S01_match_TA_DIC_only.py", index=False)