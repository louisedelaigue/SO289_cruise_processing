import subprocess

scripts_to_run = ["A01_combine_GEOMAR_CTD_data_and_nuts.py",
                  "A02_process_VINDTA_TA_DIC.py",
                  "A03_correct_VINDTA_DIC_drift.py",
                  "A04_match_TA_only_samples_with_SMB_sal_temp.py",
                  "A05_process_VINDTA_TA_only.py",
                  "A06_combine_TA_DIC_only_subsamples.py",
                  "A07_uws_match_pyroscience_smb.py",
                  "A08_uws_remove_bad_pH.py",
                  "A09_uws_estimate_alkalinity.py",
                  "A10_uws_correct_pH.py",
                  "A11_combine_all_CTD_TA_DIC_discrete_samples.py",
                  "A12_format_discrete_samples.py",
                  "A13_format_underway_discrete_samples.py",
                  "A14_format_underway_pH.py"
                  ]

for script in scripts_to_run:
    print("Running {}".format(script))
    subprocess.call(["python", script])
