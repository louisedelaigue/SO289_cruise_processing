import pandas as pd
import calkulate as calk
import PyCO2SYS as pyco2

# === ALKALINITY SAMPLES
# Import CTD data post-R2CO2 processing
TALK = pd.read_csv("data/processing/vindta/A05_SO289_UWS_TA_only_results.csv")

# Only keep data for SO289
L = TALK["bottle"].str.startswith("SO289")
TALK = TALK[L]

# Only keep UWS sub
TALK = TALK[TALK["bottle"].astype(str).map(len)>11]

# Only keep relevant columns
TALK = TALK[[
    "bottle",
    "salinity",
    "alkalinity",
    # "pH_initial"
    ]]

# Reimport datetime column
TALK_meta = pd.read_csv("data/processing/vindta/A04_match_TA_only_samples_with_SMB_sal_temp.csv")

# Merge columns
df = TALK.merge(TALK_meta, on="bottle", how="inner")

# Drop "SO289" prefix for bottle names
TALK["bottle"] = TALK["bottle"].str.replace("SO289-", "")

# === DIC SAMPLES
DIC = pd.read_excel("data/quaatro/DIC_vials/230112 DIC LOUISE DR1R1_format_friendly.xlsx")

# Only keep good data
L = DIC["Flag"]==2
DIC = DIC[L]

# Remove white space
# DIC = DIC.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# Convert to datetime
DIC["date_time"] = pd.to_datetime(DIC["date_time"], format="%d/%m/%y %H:%M")
df["date_time"] = pd.to_datetime(df["date_time"])

# Sort df
df = df.sort_values(['date_time'])
DIC = DIC.sort_values(["date_time"])

# Add DIC back to df
df = pd.merge_asof(df, DIC, on="date_time", direction="nearest", tolerance=pd.Timedelta(minutes=5))

# === CLEAN UP FINAL DF
df = df[[
    "date_time",
    "lat",
    "lon",
    "SBE45_sal",
    "SBE38_water_temp",
    # "pH_initial",
    "alkalinity",
    "DIC"
    ]]

# Calculate density of each sample at lab temperature (= 23 deg C) and sample salinity
df['density'] = calk.density.seawater_1atm_MP81(23, df['SBE45_sal'])

# Convert from umol/L to umol/kg for DIC only (K. Bakker lab analysis)
df['DIC'] = df['DIC'] / df['density']

# Drop density column
df = df.drop(columns=["density"])

# Calculate pH total (in-situ) from TA and DIC
df["pH_total_est_TA_DIC"] = pyco2.sys(
        par1=df["alkalinity"].to_numpy(),
        par2=df["DIC"].to_numpy(),
        par1_type=1,
        par2_type=2,
        opt_pH_scale=1,
        salinity=df["SBE45_sal"].to_numpy(),
        temperature=df["SBE38_water_temp"].to_numpy(),
    )["pH_total"]

# Save to .csv
df.to_csv("data/_results/SO289_underway_TA_DIC_only_results.csv", index=False)