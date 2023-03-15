import pandas as pd
import calkulate as calk

# Import sample ID with station number
# stations = pd.read_excel(
#     "data/raw_files/DIC and S samples.xlsx", sheet_name="for_looks"
# )

stations = pd.read_excel(
    "data/raw_files/son_289_ssCTD_btl.xlsx"
)

# Import all sheets from preliminary CTD bottle Excel file into one df
# ctd = pd.concat(
#     pd.read_excel(
#         "data/raw_files/Preliminary bottle data SSCTD SO289.xlsx", sheet_name=None
#     ),
#     ignore_index=True,
# )

# Add station number to df
# df = ctd.merge(stations, how="inner", left_on="Label ID", right_on="Sample_n")

# Drop useless columns
# useless_columns = ["Label ID", "Latitude_N", "Longitude_E", "Depth_m_y"]
# df.drop(columns=useless_columns, inplace=True)

# Rename columns
rn = {
    "Sample no.": "bottle",
    "Ship station":"station",
    "Bottle": "niskin",
    "Lon (deg E)": "longitude",
    "lat (deg N)": "latitude",
    "Depth (m)": "depth",
    "pressure (dbar)":"pressure",
    "Turbidity_FTU": "turbidity",
    "Oxygen (umol/kg)": "oxygen",
    "Salinity PSS-78": "salinity",
    "temp ITS-90 (deg C)": "temperature",
    "Fluorescence_mgperm3": "fluorescence",
    "Pressure_dbar": "pressure",
    "Stn_n": "station",
    "Year":"year",
    "Month":"month",
    "Day":"day",
    "Hour":"hour",
    "Minute":"minute",
    "Second":"second"
}
stations.rename(columns=rn, inplace=True)

# Reorder columns
stations = stations[
    [
        "year",
        "month",
        "day",
        "hour",
        "minute",
        "second",
        "station",
        "bottle",
        "niskin",
        "latitude",
        "longitude",
        "depth",
        "pressure",
        "salinity",
        "temperature",
        "oxygen",
        # "fluorescence",
        # "turbidity",
    ]
]

# Import nutrients
nuts = pd.read_excel(
    "data/raw_files/SO289_nutrient results_format_friendly.xlsx",
    sheet_name="SS-CTD",
    skiprows=[1],
    na_values="<LOD",
)

# Drop useless nuts columns
useless_columns = [
    "Station",
    "CTD-type",
    "Real\nDepth [m]",
    "Bottle no.",
    "TON",
    "Unnamed: 10",
]
nuts.drop(columns=useless_columns, inplace=True)

# Rename nuts columns
rn = {
    "Sample No.:": "bottle",
    "Phosphate": "phosphate",
    "Nitrite": "nitrite",
    "Silicate": "silicate",
    "Nitrate": "nitrate",
}
nuts.rename(columns=rn, inplace=True)

# Add nutrients to metadata
df = stations.merge(nuts, how="inner", on="bottle")

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
df.to_csv("data/SO289_CTD_data.csv", index=False)
