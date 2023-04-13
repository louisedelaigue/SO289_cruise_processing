import processing_scripts as ps

# Import raw continuous optode measurements (optional: process it // time-consuming)
df = ps.raw_process(
    "data/underway/SO289_UWS_continuous_file_list.xlsx",
    "data/underway/pH",
    "data/underway/SMB/SMB_data_galley.dat",
)

# Save pre BGC processing data
df.to_csv("./data/processing/optode/A07_uws_match_pyroscience_smb.csv", index=False)
