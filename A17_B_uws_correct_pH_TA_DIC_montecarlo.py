import pandas as pd
import numpy as np
import PyCO2SYS as pyco2

# Load data
subsamples = pd.read_csv("data/processing/vindta/SO289_underway_TA_DIC_only_results.csv")

# Import RMSE for TALK and DIC based on NUTS analysis
talk_rmse = 0.9189418360170623
dic_rmse = 1.9537907404909995

# Number of Monte Carlo iterations
n_iterations = 1000

# Initialize a DataFrame to store pH values
# Add 'subsample_index' to keep track of each subsample across iterations
pH_values = pd.DataFrame({
    'iteration': np.repeat(np.arange(n_iterations), len(subsamples)),
    'subsample_index': np.tile(np.arange(len(subsamples)), n_iterations),
    'pH_total_est_TA_DIC': np.zeros(n_iterations * len(subsamples))
})

# Monte Carlo simulation
for i in range(n_iterations):
    # Generate random samples for TALK and DIC within +/- RMSE
    talk_samples = subsamples['alkalinity'] + np.random.normal(0, talk_rmse, subsamples.shape[0])
    dic_samples = subsamples['DIC'] + np.random.normal(0, dic_rmse, subsamples.shape[0])

    # Calculate pH using the randomly sampled TA and DIC
    ph_results = pyco2.sys(
        par1=talk_samples.to_numpy(),
        par2=dic_samples.to_numpy(),
        par1_type=1,
        par2_type=2,
        opt_pH_scale=1,
        salinity=subsamples["SBE45_sal"].to_numpy(),
        temperature=subsamples["SBE38_water_temp"].to_numpy()
    )['pH_total']

    # Store results in DataFrame
    pH_values.loc[pH_values['iteration'] == i, 'pH_total_est_TA_DIC'] = ph_results

# Compute the mean pH for each subsample
mean_pH = pH_values.groupby('subsample_index')['pH_total_est_TA_DIC'].mean()

# Merge the mean pH back into the original DataFrame to compute differences
pH_values = pH_values.merge(mean_pH.rename('mean_pH'), on='subsample_index')

# Calculate squared differences from the mean
pH_values['squared_differences'] = (pH_values['pH_total_est_TA_DIC'] - pH_values['mean_pH'])**2

# Compute mean of squared differences (MSE) for each subsample and then take the square root (RMSE)
rmse_pH = np.sqrt(pH_values.groupby('subsample_index')['squared_differences'].mean())

# The result is a series where the index is the subsample_index and the value is the RMSE of pH for that subsample
print(rmse_pH)

#%%
# === ADD uncertainty to df of subsamples
rmse_df = rmse_pH.reset_index()
rmse_df.columns = ['subsample_index', 'pH_RMSE']
subsamples['subsample_index'] = subsamples.index  # only add this if not already present

# Merge the RMSE data with the original subsamples data
subsamples_with_uncertainty = pd.merge(subsamples, rmse_df, on='subsample_index', how='left')

# Save the merged DataFrame or perform further analysis
subsamples_with_uncertainty.to_csv("data/processing/vindta/SO289_underway_TA_DIC_only_results_with_uncertainty.csv", index=False)
