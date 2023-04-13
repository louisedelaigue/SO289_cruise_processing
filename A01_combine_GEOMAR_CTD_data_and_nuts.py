import pandas as pd
import calkulate as calk

# Import sample ID with station number
stations = pd.read_excel("data/ctd/son_289_ssCTD_btl.xlsx")

# Rename columns
rn = {
    "Sample no.": "bottle",
    "Ship station": "station",
    "Bottle": "niskin",
    "Lon (deg E)": "longitude",
    "lat (deg N)": "latitude",
    "Depth (m)": "depth",
    "pressure (dbar)": "pressure",
    "Turbidity_FTU": "turbidity",
    "Oxygen (umol/kg)": "oxygen",
    "Salinity PSS-78": "salinity",
    "temp ITS-90 (deg C)": "temperature",
    "Fluorescence_mgperm3": "fluorescence",
    "Pressure_dbar": "pressure",
    "Stn_n": "station",
    "Year": "year",
    "Month": "month",
    "Day": "day",
    "Hour": "hour",
    "Minute": "minute",
    "Second": "second",
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
    "data/ctd/SO289_nutrient results_format_friendly_LD.xlsx",
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
df.to_csv("data/processing/A01_combine_GEOMAR_CTD_data_and_nuts.csv", index=False)
