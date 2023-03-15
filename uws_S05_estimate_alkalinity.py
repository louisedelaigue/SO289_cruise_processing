import pandas as pd
import data_processing as tb

# Load pre-processed dataframe including both Pyroscience and SMB data
df = pd.read_csv('./data/processing/uws_S04_remove_bad_pH.csv')

# Estimate alkalinity
df = tb.bgc_process(df)

# Save df
df.to_csv('./data/processing/uws_S05_estimate_alkalinity.csv', index=False)
