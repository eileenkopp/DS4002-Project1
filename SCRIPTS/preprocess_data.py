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
        usecols=["fips", "DispositionCode", "OTN", "ChargeType", "Class", "CodeSection", "Charge", "DispositionDate"],
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

section_counts = (
    df["CodeSection"]
    .value_counts()
    .reset_index()
)
section_counts.columns = ["CodeSection", "count"]
section_counts["coverage_pct"] = 100 * section_counts["count"].cumsum() / section_counts["count"].sum()

print(f"Unique code sections: {len(section_counts)}")
print(section_counts.head(20))

# How many sections cover 90% of the data?
n_for_90 = (section_counts["coverage_pct"] <= 90).sum()
print(f"Top {n_for_90} sections cover 90% of records")

section_counts.to_csv("../DATA/unique_code_sections.csv", index=False)