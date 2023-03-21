import pandas as pd

# Import file 1
df = pd.read_table("data/uws/UWS/2022-03-24_003629_SO289_part_2/2022-03-24_003629_SO289_part_2.txt", skiprows=22, encoding="unicode_escape")

# Rename columns
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

df = df.rename(columns=rn)

df["datetime"] = df.date + ' ' + df.time
df["datetime"] = pd.to_datetime(df["datetime"], format="%d-%m-%Y %H:%M:%S.%f")

print(df["datetime"].dt.day.unique())
print(df["datetime"].dt.month.unique())