# This script estimates alkalinity in the South Pacific Ocean for
# underway pH data

import pandas as pd
import processing_scripts as ps

# Load pre-processed dataframe including both Pyroscience and SMB data
df = pd.read_csv("./data/processing/optode/A08_remove_bad_pH.csv")

# Estimate alkalinity
df = ps.bgc_process(df)

# Save df
df.to_csv("./data/processing/optode/A09_estimate_alkalinity.csv", index=False)
