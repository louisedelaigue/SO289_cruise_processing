# Data processing for SO289 cruise

[![DOI](https://zenodo.org/badge/563245618.svg)](https://zenodo.org/badge/latestdoi/563245618)

<img src=cruise_track.PNG width="860.5" height="405"/>

The SO289 research cruise on FS Sonne occurred during the 2022 austral autumn, traveling from Valparaiso to Noumea in the South Pacific Ocean. The primary focus was on trace element biogeochemistry and chemical oceanography, also incorporating physical and biological aspects. The mission aimed to extensively analyze the distribution, origins, and depletions of trace elements and their isotopes (TEIs) in a lesser-explored ocean region. This study sought to understand TEI biogeochemical cycles, their link to surface ocean productivity, and their role in carbon and nitrogen cycles, especially considering some TEIs serve as micronutrients. These insights are crucial for grasping the chemical foundation of marine ecosystems.

---

## Table of Contents
- [Cruise Report](#data-overview)
- [Data Overview](#data-overview)
- [Processing Steps](#processing-steps)
- [Results Files](#results-files)
- [Usage](#usage)
- [Visualisation](#visualisation)
- [Contributions and Feedback](#contributions-and-feedback)
- [Credits](#credits)
- [References](#references)
- [License](#license)

## Cruise Report
The cruise report can be found in the ```cruise_report``` folder of this repo in pdf format.

## Data Overview

- **Source**: South Pacific GEOTRACES Cruise No. SO289, Valparaiso (Chile) – Noumea (New Caledonia), GEOTRACES GP21
- **Contents**: Carbonate chemistry discrete samples were taken from the CTD (395 measurements) and the underway water system (32 measurements). A high-resolution (1 measurement every 30 seconds; 78034 measurements) time series of surface ocean pH cross-calibrated using UWS discrete samples is also available. Please be aware that high-resolution data is available only during favorable weather conditions. An alkalinity enhancement experiment was conducted on board, and the data from this experiment has been processed in this repository.
- **Time Period**:  18 February 2022 – 08 April 2022

## Processing Steps
All processing can be run at once using the ```A00_RUN_PROCESSING.py``` script. A ```requirements.txt``` file can be found in the repo. Below is a summary of each processing script.

- **Detailed processing scripts**

:warning: Please note: The SMB data, essential for the complete processing, is too large for GitHub hosting. To run the entire processing workflow, you'll need to request this file separately.

 ```A01_combine_GEOMAR_CTD_data_and_nuts.py```: Combines data received by GEOMAR - CTD and nutrients - analyzed on board.
 
 ```A02_process_VINDTA_TA_DIC.py```: Processes bottle TA/DIC (250 mL borosilicate glass bottles) analyzed on the VINDTA 3C at NIOZ.
 
 ```A03_correct_VINDTA_DIC_drift.py```: Corrects DIC dift from VINDTA coulometer. Drift correction is applied using a PCHIP through the drift in internal reference seawater samples (NUTS).

 ```A04_match_TA_only_samples_with_SMB_sal_temp.py```: Fetches data from the SMB underway thermosalinograph and matches to TA sampled in 150 mL HDPE plastic bottles.
 
 ```A05_process_VINDTA_TA_only.py```: Processes TA only (150 HDPE plastic bottles) results from the VINDTA 3C at NIOZ.

 ```A06_combine_TA_DIC_only_subsamples.py```: Combines TA only (150 HDPE plastic bottles) analysis results from the VINDTA 3C with DIC only results (12 mL exetainers vials) from the Seal QuAAtro gas-segmented continuous flow analyser. Both at NIOZ.
 
 ```A07_uws_match_pyroscience_smb.py```: Opens and combines Pyroscience files from the optode plugged into the underway, then matches the optode pH to the SMB salinograph data using date and time.
 
 ```A08_remove_bad_pH.py```: Looks at massive pH drifts to remove bad pH data.
 
 ```A09_uws_estimate_alkalinity.py```: Estimates alkalinity in the South Pacific Ocean for underway pH data using the Lee et al. (2006) equations.
 
 ```A10_uws_correct_pH.py```: Corrects continuous underway pH using an approach similar to the DIC drift correction, with a PCHIP through all pH difference in between pH(optode) and pH(subsamples), the latter calculated from TA/DIC.
 
 ```A11_combine_all_CTD_TA_DIC_discrete_samples.py```: Combines all discrete samples for TA and DIC.
  
Remaing scripts ```A12``` to ```A14``` format the data into a user-friendly .csv file.

## Results Files
Results files can be found in ```data/_results/```. Files provide the conclusive results for SO289 carbonate chemistry, encompassing TA, DIC, and a high-resolution pH time series.

- **Detailed results files**

 ```SO289_CTD_discrete_samples_V6.csv```: CTD discrete measurements for TA/DIC.
 
 ```SO289_UWS_discrete_samples_V2.csv```: Underway discrete measurements for TA/DIC.
 
 ```SO289_UWS_time_series_V2.csv```: Underway high-resolution pH time series.
 
  ```SO289_TA_enhancement_experiment_V4.csv```: Discrete measurements for alkalinity enhancement experiment.

## Usage
If you utilize data from this repository, it's imperative that you properly cite it according to the guidelines provided by the NIOZ Data Archive System (DAS). Within the NIOZ DAS, you will find the corresponding citation format and DOIs for the dataset. Ensuring correct attribution helps support the researchers and institutions that contribute to open data initiatives.

## Visualisation
The processing of VINDTA data uses package Calkulate (Humphreys and Matthews, 2023). After running calkulate() (or calibrate() and solve()) on the data, Calkulate contains some plotting functions to help visualise the analysis. These can be found in ```/figs/vindta``` and ```/figs/vindta_TA_only```. DIC drift corrections are also available in ```/figs/vindta/drift_correction```.

<img src=figs/A08_remove_bad_pH.png width="600" height="450"/>

<img src=figs/A10_uws_correct_pH.png width="600" height="450"/>

## Contributions and Feedback
We highly value the community's insights and feedback on this processing repository. If you have remarks or suggestions, please directly address them to Louise Delaigue at ```louise.delaigue@nioz.nl```. Alternatively, you're encouraged to raise an issue on GitHub to facilitate discussion and potential improvements.

## Credits
Special acknowledgment goes to Dr. Chris Galley and Paul Battermann, who conducted the sampling aboard the FS Sonne. Dr. Tom Browning led the TA enhancement experiment on board. The TA/DIC and TA only analyses were handled by Louise Delaigue, Yasmina Ourradi, and Sharyn Ossebar. DIC only samples were handled by Karel Bakker. All lab analysis was conducted at the NIOZ Royal Netherlands Institute for Sea Research. The processing code was implemented by Louise Delaigue. Additionally, the entire analysis and processing workflow was under the oversight of Dr. Matthew Humphreys.
## References
- **Humphreys, M. P. and Matthews, R. S. (2023). Calkulate: total alkalinity from titration data in Python. Zenodo. doi:10.5281/zenodo.2634304.**
- **Lee, K., Tong, L. T., Millero, F. J., Sabine, C. L., Dickson, A. G., Goyet, C., Park, G.-H., Wanninkhof, R., Feely, R. A., and Key, R. M. (2006), Global relationships of total alkalinity with salinity and temperature in surface waters of the world's oceans, Geophys. Res. Lett., 33, L19605, doi:10.1029/2006GL027207.**

## License
This repository is licensed under the GNU General Public License v3.0 (GPL-3.0), ensuring that the software remains free and open, with the source code available for transparency and modification.
