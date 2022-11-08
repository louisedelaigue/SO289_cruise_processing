import pandas as pd
import calkulate as calk

# Import sample ID with station number
stations = pd.read_excel(
    "data/raw_files/DIC and S samples.xlsx", sheet_name="for_looks"
)

# Import all sheets from preliminary CTD bottle Excel file into one df
ctd = pd.concat(
    pd.read_excel(
        "data/raw_files/Preliminary bottle data SSCTD SO289.xlsx", sheet_name=None
    ),
    ignore_index=True,
)

# Add station number to df
df = ctd.merge(stations, how="inner", left_on="Label ID", right_on="Sample_n")

# Drop useless columns
useless_columns = ["Sample_n", "Latitude_N", "Longitude_E", "Depth_m_y"]
df.drop(columns=useless_columns, inplace=True)

# Rename columns
rn = {
    "Label ID": "sample",
    "Bottle_Number": "niskin",
    "Longitude_deg_E": "longitude",
    "Latitude_deg_N": "latitude",
    "Depth_m_x": "depth",
    "Turbidity_FTU": "turbidity",
    "Oxygen_umolperkg": "oxygen",
    "Salinity_PSU": "salinity",
    "Temperature_oC": "temperature",
    "Fluorescence_mgperm3": "fluorescence",
    "Pressure_dbar": "pressure",
    "Stn_n": "station",
}
df.rename(columns=rn, inplace=True)

# Reorder columns
df = df[
    [
        "sample",
        "station",
        "niskin",
        "latitude",
        "longitude",
        "depth",
        "pressure",
        "salinity",
        "temperature",
        "oxygen",
        "fluorescence",
        "turbidity",
    ]
]

# Import nutrients
nuts = pd.read_excel(
    "data/raw_files/SO289_nutrient results_format_friendly.xlsx",
    sheet_name="SS-CTD",
    skiprows=[1],
    na_values="<LOD"
)

# Drop useless nuts columns
useless_columns = ["Station", "CTD-type", "Real\nDepth [m]", "Bottle no.", "TON", "Unnamed: 10"]
nuts.drop(columns=useless_columns, inplace=True)

# Rename nuts columns
rn = {
    "Sample No.:": "sample",
    "Phosphate": "phosphate",
    "Nitrite": "nitrite",
    "Silicate": "silicate",
    "Nitrate": "nitrate",
}
nuts.rename(columns=rn, inplace=True)

# Add nutrients to metadata
df = df.merge(nuts, how="inner", on="sample")

# Calculate density of each sample
df["density"] = calk.density.seawater_1atm_MP81(23, df["salinity"])

# Convert nutrients from umol/L to umol/kg
df["phosphate"] = df["phosphate"] / df["density"]
df["nitrite"] = df["nitrite"] / df["density"]
df["silicate"] = df["silicate"] / df["density"]
df["nitrate"] = df["nitrate"] / df["density"]

# Sort df by station and niskin
df.sort_values(by=["station", "niskin"], inplace=True)

# Save as csv
df.to_csv("data/CTD_data.csv", index=False)
