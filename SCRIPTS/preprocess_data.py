"""
This file outlines our data cleaning process. We first access the data, and concatenate only the columns needed for our analysis.
We drop rows which contain duplicated OTN numbers so that we aren't double counting any court cases
We make sure to remove any human errors / inconsistencies in the "charge" free text column, including trailing whitespaces or extraneous characters.
We then count all the unique CodeSections, and generate a csv file containing only the unique codes and their frequency counts, which gets used to label the data
We then apply our labeling logic, and discard any rows in which there is no matching category for a crime code.
After running this script, our data is now ready to be used by the model!
Outputs of this file include: 
    - unique_code_sections.csv
    - labeled_code_sections.csv
    - data_cleaned.csv
"""

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