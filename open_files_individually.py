import pandas as pd, numpy as np

chunky = pd.read_table('data/uws/SMB/SMB_data_galley.dat',
                 chunksize=150000,
                 na_values=[9999, 9],
                 sep = ',',
                 encoding= 'unicode_escape',
                 low_memory=False)


# create empty list to hold cleaned up chunks
smb_list = []

# rename temp_source column to python friendly, then only keep where 
# temp_source has data, then store cleaned up chunks into smb_list
for file in chunky:
    file = file.drop([file.index[0], file.index[1]])
    file.reset_index(drop=True)
    rn = {
       'SMB.RSSMB.T_SBE38':'SBE38_water_temp'
       }
    file.rename(rn, axis=1, inplace=True)
    # file.dropna(subset=['SBE38_water_temp'], inplace=True)
    smb_list.append(file)

# create 1 df holding all cleaned up smb data
smb = pd.concat(smb_list)
    

#%%

text = pd.read_table("data/uws/UWS/2022-02-28_230025/2022-02-28_230025.txt", skiprows=22, encoding="unicode_escape")

rn = {
      "Date [A Ch.1 Main]":"date",
      "Time [A Ch.1 Main]":"time",
      " dt (s) [A Ch.1 Main]":"sec",
      "pH [A Ch.1 Main]":"pH_cell",
      "Sample Temp. (°C) [A Ch.1 CompT]":"temp_cell",
      "dphi (°) [A Ch.1 Main]":"dphi",
      "Signal Intensity (mV) [A Ch.1 Main]":"signal_intensity",
      "Ambient Light (mV) [A Ch.1 Main]":"ambient_light",
      "ldev (nm) [A Ch.1 Main]":"ldev",
      "Status [A Ch.1 Main]":"status_ph",
      "Status [A Ch.1 CompT]":"status_temp",
       }

text = text.rename(rn, axis=1)
text['date_time'] = np.nan
text.date_time = text.date + ' ' + text.time

text.drop(columns=["Date [Comment]",
                "Time [Comment]",
                "Comment",
                "date",
                "time",
                "pH (pH) [A Ch.1 Main]",
                "Date [A Ch.1 CompT]",
                "Time [A Ch.1 CompT]",
                " dt (s) [A Ch.1 CompT]",
                "Date [A T1]",
                "Time [A T1]",
                " dt (s) [A T1]",
                "Sample Temp. (°C) [A T1]",
                "Status [A T1]",
                "Unnamed: 23",
                "Unnamed: 24",
                "Unnamed: 25",
                "Unnamed: 26",
                "Unnamed: 27",
                "Unnamed: 28",
                "Unnamed: 29"],
                inplace=True)
text.dropna()

text = text[[
                                  'date_time',
                                  'sec',
                                  'pH_cell',
                                  'temp_cell',
                                  'dphi',
                                  'signal_intensity',
                                  'ambient_light',
                                  'ldev',
                                  'status_ph',
                                  'status_temp']]

#%% do above cell but with tools function

from data_processing import read_pyrosci

data_dict, file_list = read_pyrosci("data/uws/SO289_UWS_continuous_file_list.xlsx", "data/uws/UWS")