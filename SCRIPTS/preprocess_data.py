#Process would be to assign labels in a certain manner
# 


#use text charge to assign into one of our category via tdf-if, 
#tdf-if assigns into our pre-decided category, 
#using newly assigned category, assign actual training data label, 
#then have model guess

import pandas as pd
import glob
import os
import matplotlib.pyplot as plt

input_folder = "../DATA/court_case_data"
files = glob.glob(os.path.join(input_folder, "*.csv"))

dfs = []

for file in files:
    temp = pd.read_csv(
        file,
        usecols=["fips", "DispositionCode", "OTN", "ChargeType", "Class"],
        low_memory=False
    )

    temp = temp.dropna(subset=["DispositionCode"])
    dfs.append(temp)

# Combine all 7 files
df = pd.concat(dfs, ignore_index=True)

# Remove duplicate OTN records
before = len(df)
df = df.drop_duplicates(subset="OTN")

print(f"Records before removing duplicates: {before:,}")
print(f"Records after removing duplicates: {len(df):,}")
