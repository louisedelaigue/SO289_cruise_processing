# This script combines all discrete samples

import pandas as pd

# Load results from lab analysis for TA and DIC
ta_dic = pd.read_csv("data/processing/vindta/SO289_CTD_TA_DIC_results.csv")

# Load CTD data
ctd = pd.read_csv("data/processing/A01_combine_GEOMAR_CTD_data_and_nuts.csv")

# Only keep SO289 samples
L = ta_dic.bottle.str.startswith("SO289")
ta_dic = ta_dic[L]

# Remove "SO289" string
ta_dic["bottle"] = [b.replace("SO289-", "") for b in ta_dic["bottle"]]

# Remove subsample
ta_dic = ta_dic[ta_dic["bottle"].astype(str).map(len)==5]

# Convert bottle column to numeric
ta_dic["bottle"] = ta_dic["bottle"].astype("int64")

# Only keep relevant columns
ta_dic = ta_dic[[
    "bottle",
    "alkalinity",
    "dic_corrected"
    ]]

# Add alkalinity and DIC to CTD data
ctd = ctd.merge(ta_dic, on="bottle", how="outer")

# === TA ONLY - Load results from lab analysis for TA only
ta = pd.read_csv("data/processing/vindta/SO289_CTD_TA_only_results.csv")

# Only keep SO289 samples
L = ta.bottle.str.startswith("SO289")
ta = ta[L]

# Remove "SO289" string
ta["bottle"] = [b.replace("SO289-", "") for b in ta["bottle"]]

# Remove subsamples
ta = ta[ta["bottle"].astype(str).map(len)==5]

# Convert bottle column to numeric
ta["bottle"] = ta["bottle"].astype("int64")

# Only keep relevant columns
ta = ta[[
    "bottle",
    "alkalinity",
    ]]

# Rename alkalinity column
ta = ta.rename(columns={"alkalinity":"TA_only"})

# Add alkalinity only CTD data
ctd = ctd.merge(ta, on="bottle", how="outer")

# === DIC ONLY  - Load results from lab analysis for DIC only
dic = pd.read_excel("data/quaatro/DIC_vials/230112 DIC LOUISE ER1R1_format_friendly.xlsx")

# Only keep good data
L = dic["Flag"]==2
dic = dic[L]

# Convert bottle column to numeric
dic["bottle"] = dic["bottle"].astype("int64")

# Only keep relevant columns
dic = dic[[
    "bottle",
    "DIC",
    ]]

# Rename DIC column
dic = dic.rename(columns={"DIC":"DIC_only"})

# Add DIC only to CTD data
ctd = ctd.merge(dic, on="bottle", how="outer")

# Save as .csv
ctd.to_csv("data/processing/vindta/SO289_CTD_data_TA_DIC_combined.csv", index=False)
