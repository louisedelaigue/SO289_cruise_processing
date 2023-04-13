from processing_scripts import read_pyrosci
from processing_scripts import logbook
from processing_scripts import smb
from processing_scripts import alkalinity

def raw_process(datasheet_filepath, txt_filepath, smb_filepath):
    data_dict, file_list = read_pyrosci(datasheet_filepath, txt_filepath)
    data = logbook(data_dict, file_list)
    df = smb(data, smb_filepath)
    return df

def bgc_process(df):
    # dat_sal = salinity(df)
    dat_alk = alkalinity(df)
    return dat_alk
