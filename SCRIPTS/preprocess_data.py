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

columns_to_keep = [
    "HearingDate", "HearingResult", "HearingType",
    "fips", "Filed", "Commencedby",
    "Sex", "Race", "Address",
    "Charge", "CodeSection", "ChargeType", "Class",
    "OffenseDate", "ArrestDate",
    "DispositionDate", "ConcludedBy",
    "SentenceTime", "SentenceSuspended", "FineAmount", "Costs",
    "OTN", "person_id",
]

dfs = []

for file in files:
    temp = pd.read_csv(
        file,
        usecols=columns_to_keep,
        low_memory=False
    )
    dfs.append(temp)

# Combine all files
df = pd.concat(dfs, ignore_index=True)

# Remove duplicate OTN records (OTN is the unique case identifier)
before = len(df)
df = df.drop_duplicates(subset="OTN")

print(f"Records before removing duplicates: {before:,}")
print(f"Records after removing duplicates: {len(df):,}")

# --- Additional cleaning steps ---

# Strip stray whitespace from all text columns
str_cols = df.select_dtypes(include="object").columns
for col in str_cols:
    df[col] = df[col].str.strip()

# Standardize casing on the categorical fields so e.g. "felony" and "Felony"
# aren't treated as different categories downstream
for col in ["ChargeType", "Class"]:
    df[col] = df[col].astype(str).str.upper()

# Drop rows missing an identifier we need for joining/matching later
before_missing = len(df)
df = df.dropna(subset=["OTN", "fips"])
removed_missing = before_missing - len(df)
print(f"Records after dropping missing OTN/fips: {len(df):,} (removed {removed_missing:,})")

# Drop rows where a cleaned field ended up as an empty string
df = df[(df["ChargeType"] != "") & (df["Class"] != "")]

# fips is unpadded in the source (e.g. 99), pad to standard 3-digit code
df["fips"] = df["fips"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(3)

# Quick sanity check on category spread before moving to the labeling step
print("\nUnique ChargeType values:", df["ChargeType"].nunique())
print("Unique Class values:", df["Class"].nunique())

# Missingness report -- shows % blank per column so you can decide, per column,
# whether a blank is "bad data" (drop/fill) or structurally meaningful
# (e.g. no SentenceTime because the case was Nolle Prosequi'd)
missing_pct = (df.isna().mean() * 100).round(2).sort_values(ascending=False)
print("\nPercent missing by column:")
print(missing_pct.to_string())

# Save the cleaned dataset for the next step in the pipeline
output_path = os.path.join(input_folder, "cleaned_court_case_data.csv")
df.to_csv(output_path, index=False)
print(f"\nCleaned data saved to: {output_path}")
