import pandas as pd

# Import UWS subsample list
samples = pd.read_csv("data/list_uws_samples.csv")

# Only keep SO289 samples
L = samples.bottle.str.startswith("SO289")
samples = samples[L]

# Only keep UWS subsamples
samples = samples[samples["bottle"].astype(str).map(len)>11]

# For now, assign midnight to sample with no hour or minute
samples.loc[samples["bottle"]=="SO289-31032022-NA-NA", "bottle"] = "SO289-31032022-00-00"

# Create a datetime column
samples["day"] = [s.split("-")[1][:2] for s in samples["bottle"]]
samples["month"] = [s.split("-")[1][2:4] for s in samples["bottle"]]
samples["year"] = [s.split("-")[1][4:] for s in samples["bottle"]]
samples["hour"] = [s.split("-")[2] for s in samples["bottle"]]
samples["minute"] = [s.split("-")[3] for s in samples["bottle"]]

samples["date_time"] = pd.to_datetime(samples[['day', 'month', 'year', 'hour', 'minute']])

# Only keep relevant columns
samples = samples[[
    "bottle",
    "date_time"
    ]]

# Load SMB data and match to UWS subsamples
chunky = pd.read_table("data/uws/SMB/SMB_data_galley.dat",
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

# rename headers with python friendly names
rn = {
      'date time':'date_time',
      'Weatherstation.PDWDC.Airtemperature':'WS_airtemp',
      'Weatherstation.PDWDC.Barometric':'WS_baro',
      'Weatherstation.PDWDC.Course':'WS_course',
      'Weatherstation.PDWDC.Date':'WS_date',
      'Weatherstation.PDWDC.Heading':'WS_heading',
      'Weatherstation.PDWDC.Humidity':'WS_humidity',
      'Weatherstation.PDWDC.Latitude':'WS_lat',
      'Weatherstation.PDWDC.Longitude':'WS_lon',
      'Weatherstation.PDWDC.Longwave':'WS_longwave',
      'Weatherstation.PDWDC.NormalizedTo':'WS_normto',
      'Weatherstation.PDWDC.Pyrogeometer':'WS_pyrogeometer',
      'Weatherstation.PDWDC.SensorValue':'WS_sensorvalue',
      'Weatherstation.PDWDC.Sentence':'WS_sentence',
      'Weatherstation.PDWDC.Shortwave':'WS_shortwave',
      'Weatherstation.PDWDC.Speed':'WS_speed',
      'Weatherstation.PDWDC.Timestamp':'WS_timestamp',
      'Weatherstation.PDWDC.Watertemperature':'WS_watertemp',
      'Weatherstation.PDWDC.Winddirection_rel':'WS_winddirection_rel',
      'Weatherstation.PDWDC.Winddirection_true':'WS_winddirection_true',
      'Weatherstation.PDWDC.Windspeed_rel':'WS_windspeed_rel',
      'Weatherstation.PDWDC.Windspeed_true':'WS_windspeed_true',
      'Weatherstation.PDWDC.Windspeed_true_Bft':'WS_windspeed_true_bft',
      'SMB.RSSMB.Chl':'chl',
      'SMB.RSSMB.C_SBE45':'SBE_45_C',
      'SMB.RSSMB.Date':'date',
      'SMB.RSSMB.Delay':'delay',
      'SMB.RSSMB.Depth':'depth',
      'SMB.RSSMB.EW':'ew',
      'SMB.RSSMB.Flow':'flow',
      'SMB.RSSMB.Latitude':'lat',
      'SMB.RSSMB.Longitude':'lon',
      'SMB.RSSMB.Name':'smb_name',
      'SMB.RSSMB.NS':'ns',
      'SMB.RSSMB.RVK':'system',
      'SMB.RSSMB.Sal_SBE45':'SBE45_sal',
      'SMB.RSSMB.Sentence':'sentence',
      'SMB.RSSMB.SN':'sn',
      'SMB.RSSMB.SV_SBE45':'SBE45_sv',
      'SMB.RSSMB.SV_insito':'insitu_sv',
      'SMB.RSSMB.Status':'smb_status',
      'SMB.RSSMB.SV_AML':'smb_sv_aml',
      'SMB.RSSMB.T_SBE45':'SBE45_water_temp',
      'SMB.RSSMB.Time':'smb_time',
      'SMB.RSSMB.Tur':'smb_tur'
      }

smb.rename(rn, axis=1, inplace=True)

# Make sure datetime is in pandas datetime
smb["date_time"] = pd.to_datetime(smb["date_time"])

# convert SMB date format to match PyroSci date format
# def date_convert(date_to_convert):
#       return datetime.datetime.strptime(date_to_convert, "%Y/%m/%d %H:%M:%S").strftime("%d-%m-%Y %H:%M:%S")
# smb['date_time'] = smb['date_time'].apply(date_convert)

# convert temperature and salinity columns to numeric
smb.SBE38_water_temp = pd.to_numeric(smb.SBE38_water_temp)
smb.SBE45_sal = pd.to_numeric(smb.SBE45_sal)

# import SMB back into samples df
smb = smb.sort_values(['date_time'])
samples = samples.sort_values(["date_time"])

df = pd.merge_asof(samples, smb, on='date_time', direction="nearest", tolerance=pd.Timedelta(minutes=5))

# Only keep relevant columns
df = df[[
    "bottle",
    "date_time",
    "SBE45_sal",
    "SBE38_water_temp"    
    ]]
        
# Convert to numeric
df["SBE38_water_temp"] = pd.to_numeric(df["SBE38_water_temp"])
df["SBE45_sal"] = pd.to_numeric(df["SBE45_sal"])

# Save to .csv
df.to_csv("data/processing/uws_S06_match_samples_SMB_sal_temp.csv")
