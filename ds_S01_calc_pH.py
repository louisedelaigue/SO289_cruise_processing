import pandas as pd
import PyCO2SYS as pyco2

# Import CTD data post-R2CO2 processing
lab = pd.read_csv("data/SO289-64PE503_results_recalibrated.csv")

# Only keep data for SO290
L = lab["bottle"].str.startswith("SO289")
lab = lab[L]

# Only keep relevant columns
lab = lab[[
    "bottle",
    "alkalinity",
    "dic"    
    ]]

# Drop "SO289" prefix for bottle names
lab["bottle"] = lab["bottle"].str.replace("SO289-", "")

# Convert to numeric
# lab["bottle"] = pd.to_numeric(lab["bottle"])

# Add results to CTD data
df = pd.read_csv("data/SO289_CTD_data.csv")

# Add columns to results
final = df.merge(lab, on="bottle")


# Calculate pH from TA and DIC(corr)
# carb_dict = pyco2.sys(df.alkalinity, df.dic_corrected, 1, 2, 
#                       salinity=df.salinity,
#                       temperature=df.temperature,
#                       temperature_out=df.temperature,
#                       pressure=0,
#                       pressure_out=df.pressure,
#                       )

# # save in-situ pH to df
# df['pH_insitu_ta_dic(corr)'] = carb_dict['pH_total_out']