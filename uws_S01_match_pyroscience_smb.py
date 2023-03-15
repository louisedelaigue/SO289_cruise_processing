import pandas as pd
import data_processing as tb

# Import raw continuous optode measurements (optional: process it // time-consuming)
df = tb.raw_process("data/uws/SO289_UWS_continuous_file_list.xlsx", "data/uws/UWS", "data/uws/SMB/SMB_data_galley.dat")

# Save pre BGC processing data
df.to_csv('./data/processing/preprocessing_uws_data.csv', index=False)

# Correct salinity and estimate alkalinity
df = tb.bgc_process(df)

# Save raw UWS data
# df.to_csv('./data/processing/raw_uws_data.csv', index=False)

# df = pd.read_table("data/uws/UWS/2022-03-24_003629_SO289_part_2/2022-03-24_003629_SO289_part_2.txt", skiprows=22, encoding="unicode_escape")