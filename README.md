# Data processing for SO289 cruise

<img src=cruise_track.PNG width="860.5" height="405"/>

The SO289 research cruise on FS Sonne occurred during the 2022 austral autumn, traveling from Valparaiso to Noumea in the South Pacific Ocean. The primary focus was on trace element biogeochemistry and chemical oceanography, also incorporating physical and biological aspects. The mission aimed to extensively analyze the distribution, origins, and depletions of trace elements and their isotopes (TEIs) in a lesser-explored ocean region. This study sought to understand TEI biogeochemical cycles, their link to surface ocean productivity, and their role in carbon and nitrogen cycles, especially considering some TEIs serve as micronutrients. These insights are crucial for grasping the chemical foundation of marine ecosystems.

---

## Table of Contents
- [Cruise Report](#data-overview)
- [Data Overview](#data-overview)
- [Processing Steps](#processing-steps)
- [Usage](#usage)
- [Scripts and Notebooks](#scripts-and-notebooks)
- [Output and Visualization](#output-and-visualization)
- [Contributing](#contributing)
- [Credits](#credits)
- [License](#license)

---
## Cruise Report

The cruise report can be found in the ```cruise_report``` folder of this repo in pdf format.

## Data Overview

- **Source**: South Pacific GEOTRACES Cruise No. SO289, Valparaiso (Chile) – Noumea (New Caledonia), GEOTRACES GP21
- **Contents**: Discrete samples were taken from the CTD (77 measurements) and the underway water system. A high-resolution (1 measurement every 30 seconds) time series of surface ocean pH cross-calibrated using UWS discrete samples is also available.
- **Time Period**:  18 February 2022 – 08 April 2022

---

## Processing Steps

All processing can be run at once using the ```A0_RUN_PROCESSING.py``` script. Below is a summary of each processing script.

 ```A01_combine_GEOMAR_CTD_data_and_nuts.py```: Combines data received by GEOMAR - CTD and nutrients - analyzed on board.
 ```A02_process_VINDTA_TA_DIC.py```: Processes bottle TA/DIC (250 mL) analyzed on the VINDTA 3C at NIOZ.
 ```A03_correct_VINDTA_DIC_drift.py```: Corrects DIC dift from VINDTA coulometer. Drift correction is applied using a PCHIP through the drift in internal reference seawater samples (NUTS).
 # analysis throughout the day
 **Normalization/Standardization**: If applicable, detail the process.
 **Feature Extraction**: Discuss any new features or metrics derived from the raw data.
... (and so on for other processing steps)

---

## Usage

Instructions on how to use the scripts or notebooks to process your own cruise data.

```bash
# If there are commands to run, list them here
python your_script.py --input data.csv --output processed_data.csv
