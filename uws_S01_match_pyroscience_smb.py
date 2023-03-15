import data_processing as tb

# Import raw continuous optode measurements (optional: process it // time-consuming)
df = tb.raw_process("data/uws/SO289_UWS_continuous_file_list.xlsx", "data/uws/UWS", "data/uws/SMB/SMB_data_galley.dat")

# Save pre BGC processing data
df.to_csv('./data/processing/uws_S01_match_pyroscience_smb.csv', index=False)
