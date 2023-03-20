import pandas as pd, numpy as np
from scipy.interpolate import PchipInterpolator

# Import UWS continuous pH data
df = pd.read_csv('data/processing/uws_S05_estimate_alkalinity.csv')

# Import subsamples
subsamples = pd.read_csv('data/processing/ds_S02_calculate_pH_total')

# Convert columns to datetime objects
df['date_time'] = pd.to_datetime(df['date_time'])
subsamples['date_time'] = pd.to_datetime(subsamples['date_time'])

# === SUBSAMPLES AND CONTINUOUS pH MATCH
# Reindex subsamples to match continuous pH data based on datetime
nearest = df.set_index('date_time').reindex(subsamples.set_index('date_time').index, method='nearest').reset_index()

# Add continuous pH data points corresponding to subsamples
# based on date and time
point_location = subsamples['date_time'].tolist()
subsamples['pH_optode'] = np.nan
for location in point_location:
    subsamples.loc[subsamples['date_time']==location, 'pH_optode'] = subsamples['date_time'].map(nearest.set_index('date_time')['pH_insitu_ta_est'])

# === pH OFFSET CALCULATION
# Calculate offset between pH(TA/DIC) and pH(initial_alkalinity)
subsamples['offset'] = abs(subsamples['pH_total_est_TA_DIC'] - subsamples['pH_optode'])
offset = subsamples['offset'].mean()

subsamples['pH_corr'] = subsamples['pH_total_est_TA_DIC'] + offset

# Subtract pH(initial_alkalinity, corr) from pH(optode)
subsamples['diff'] = abs(subsamples['pH_total_est_TA_DIC'] - subsamples['pH_optode'])

# Remove where above difference is nan (PCHIP requirement)
L = subsamples['diff'].isnull()
subsamples = subsamples[~L]

# PCHIP difference points over date_time range in df
subsamples = subsamples.sort_values(by=['date_time'], ascending=True)
interp_obj = PchipInterpolator(subsamples['date_time'], subsamples['diff'], extrapolate=False)
df['pchip_pH_difference'] = interp_obj(df['date_time'])

# === CORRECTION OF pH CONTINUOUS DATA
# Correct pH(optode) using PCHIP values
df['pH_optode_corrected'] = df['pH_insitu_ta_est'] - df['pchip_pH_difference']


# === SIMPLE MOVING AVERAGE
# Compute simple moving average (SMA) over period of 30 minutes
df["SMA"] = df["pH_optode_corrected"].rolling(60, min_periods=1).mean()

# Save to .csv
df.to_csv("data/processing/uws_S07_correct_pH.csv", index=False)
