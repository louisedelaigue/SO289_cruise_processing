import pandas as pd

# from data_processing import read_pyrosci


def logbook(data_dict, file_list):
    """Apply logbook notes from cruise SO279 to Pyroscience DataFrame."""

    # for all files, ignore first 20 min for optode stabilization
    for file in file_list:
        L = data_dict[file].sec > 1200
        data_dict[file] = data_dict[file][L]
        data_dict[file]["date_time"] = pd.to_datetime(
            data_dict[file].date_time, format="%d-%m-%Y %H:%M:%S.%f"
        )

    # turn dict into single df
    data = pd.concat(data_dict.values(), ignore_index=True)

    # drop ms
    data["date_time"] = data["date_time"].apply(
        lambda x: x.strftime("%d-%m-%Y %H:%M:%S")
    )

    return data
