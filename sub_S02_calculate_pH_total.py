import pandas as pd
import PyCO2SYS as pyco2

# Import CTD data post-R2CO2 processing
df = pd.read_csv("data/processing/sub_S01_match_TA_DIC_only.csv")

# Calculate pH total from TA and DIC
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
df.to_csv("data/processing/sub_S02_calculate_pH_total.csv", index=False)