import PyCO2SYS as pyco2

def alkalinity(data):
    df = data.copy()

    def ta_zone1(SSS, SST):
        """Estimate TA for cruise SO289"""
        return (
            2305 
            + 58.66 * (SSS - 35) 
            + 2.32 * (SSS - 35)**2 
            - 1.41 * (SST - 20) 
            + 0.040 * (SST - 20)**2
            )
    
    # create new column with results in dataset
    df['ta_est'] = ta_zone1(df.SBE45_sal, df.SBE38_water_temp)
    
    # recalculate pH at in-situ temperature (SBE38) using estimated TA
    carb_dict = pyco2.sys(df.ta_est, df.pH_cell, 1, 3, 
                          salinity=df.SBE45_sal,
                          temperature=df.temp_cell,
                          temperature_out=df.SBE38_water_temp,
                          pressure=0,
                          pressure_out=3,
                          opt_pH_scale=1,
                          opt_k_carbonic=16,
                          opt_total_borate=1
                          )
    
    # save in-situ pH to df
    df['pH_insitu_ta_est'] = carb_dict['pH_total_out']
    
    return df
