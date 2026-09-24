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
import re

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

# Additional cleaning steps 

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

# Additional cleaning + labeling (appended)
# Deeper cleaning of the free-text "Charge" column (beyond the plain strip above -- collapses internal whitespace and drops stray non-printable characters), then unique-CodeSection counting, rule-based category labeling, and discarding rows with no matching category.

OUTPUT_DIR = "../DATA"
UNIQUE_SECTIONS_PATH = os.path.join(OUTPUT_DIR, "unique_code_sections.csv")
LABELED_SECTIONS_PATH = os.path.join(OUTPUT_DIR, "labeled_code_sections.csv")
CLEANED_DATA_PATH = os.path.join(OUTPUT_DIR, "data_cleaned.csv")


def clean_charge_text(raw):
    """Normalize the free-text 'Charge' column: strip whitespace, collapse
    internal whitespace runs, and drop stray non-printable/extraneous
    characters that come from inconsistent data entry."""
    if pd.isna(raw):
        return raw
    s = str(raw).strip()
    s = re.sub(r"\s+", " ", s)          # collapse repeated/odd whitespace
    s = re.sub(r"[^\x20-\x7E]", "", s)  # drop non-printable / non-ASCII junk
    s = s.strip(" .,-_")                # strip stray leading/trailing punctuation
    return s


def normalize_code_section(raw):
    if pd.isna(raw):
        return None
    s = str(raw).strip().upper()

    # multi-section entries -> take the first non-empty part
    # ("18.2-91/18.2-26" -> "18.2-91", but also guard against a leading
    # delimiter like "/46.2-300" -> "46.2-300")
    parts = [p.strip() for p in re.split(r"[/&]", s) if p.strip()]
    s = parts[0] if parts else ""

    # strip a leading subsection-letter prefix like "A.18.2-266" -> "18.2-266"
    s = re.sub(r"^[A-Z]\.\s*", "", s)

    # strip trailing parenthetical subsection refs like "18.2-456(A)(6)" -> "18.2-456"
    s = re.sub(r"\(.*\)$", "", s).strip()

    return s if s else None


def parse_section_num(num_str):
    """Parse a Virginia Code section number into a comparable tuple."""
    parts = num_str.split(".")
    main = int(parts[0])
    sub = int(parts[1]) if len(parts) > 1 and parts[1] != "" else 0
    return (main, sub)


def in_range(num_tuple, lo_str, hi_str):
    return parse_section_num(lo_str) <= num_tuple <= parse_section_num(hi_str)


def rule_based_category(norm):
    if not isinstance(norm, str) or not norm:
        return None

    # Title 19.2 = Criminal Procedure -- NOT an offense type.
    # High-volume, must be its own bucket, not "other."
    if norm.startswith("19.2-306"):
        return "probation_violation"
    if norm.startswith("19.2-128"):
        return "failure_to_appear"
    if norm.startswith("19.2"):
        return "procedural_other"

    # Title 53.1 = Corrections (escape, prisoner offenses)
    if norm.startswith("53.1"):
        return "corrections_related"

    # Title 16.1 = Juvenile & Domestic Relations procedure
    if norm.startswith("16.1"):
        return "juvenile_family"

    # Title 54.1 = drug-related professional/controlled substance provisions
    if norm.startswith("54.1"):
        return "drug"

    # Title 46.2 = Motor Vehicle code
    if norm.startswith("46.2"):
        return "traffic"

    # Title 40.1, Chapter 5 (Child Labor) -- 40.1-103
    if norm.startswith("40.1-103"):
        return "child_abuse"

    # Title 3.2, Chapter 65, Article 9 -- animal cruelty/fighting.
    if norm.startswith("3.2-65"):
        return "animal_cruelty"

    # Title 18.2 = Crimes and Offenses Generally -- range-match on the numeric part
    m = re.match(r"18\.2-(\d+(?:\.\d+)?)", norm)
    if m:
        n = parse_section_num(m.group(1))
        if in_range(n, "30", "58"):
            return "violent"
        elif in_range(n, "61", "67.10"):
            return "sexual_offense"
        elif in_range(n, "89", "160.1"):
            return "property"
        elif in_range(n, "168", "231"):
            return "fraud_financial"
        elif in_range(n, "247", "265.5"):
            return "drug"
        elif in_range(n, "266", "272"):
            return "dui_traffic_criminal"
        elif in_range(n, "279", "311"):
            return "weapons"
        elif in_range(n, "355", "371"):
            return "juvenile_family"
        elif in_range(n, "372", "390.2"):
            return "public_order"
        elif in_range(n, "456", "487"):
            return "obstruction_justice"

    return None  # unmatched -> needs manual review


# Deeper cleaning pass on "Charge", on top of the plain strip already done above
df["Charge"] = df["Charge"].apply(clean_charge_text)

# Count unique CodeSections and save frequency table
section_counts = df["CodeSection"].value_counts().reset_index()
section_counts.columns = ["CodeSection", "count"]
section_counts["coverage_pct"] = (
    100 * section_counts["count"].cumsum() / section_counts["count"].sum()
)

print(f"\nUnique code sections: {len(section_counts)}")
print(section_counts.head(20))

n_for_90 = (section_counts["coverage_pct"] <= 90).sum()
print(f"Top {n_for_90} sections cover 90% of records")

section_counts.to_csv(UNIQUE_SECTIONS_PATH, index=False)

# Apply labeling logic on the NORMALIZED section (not the raw CodeSection).
# Different raw strings (e.g. "18.2-456(A)(6)" and "18.2-456") can normalize
# to the same norm_section, so we label at the norm_section level: compute
# the category once per unique norm_section, then attach it back to every
# raw CodeSection that shares it.
section_counts["norm_section"] = section_counts["CodeSection"].apply(normalize_code_section)

norm_counts = (
    section_counts.groupby("norm_section", dropna=False)["count"]
    .sum()
    .reset_index()
)
norm_counts["category_auto"] = norm_counts["norm_section"].apply(rule_based_category)

# Attach the norm_section-level category back onto the raw-section table
# purely for the human-readable labeled_code_sections.csv output.
section_counts = section_counts.merge(
    norm_counts[["norm_section", "category_auto"]], on="norm_section", how="left"
)

total_records = norm_counts["count"].sum()
matched_records = norm_counts.loc[norm_counts["category_auto"].notna(), "count"].sum()

print(f"\nUnique normalized sections: {len(norm_counts):,}")
print(f"Total records represented: {total_records:,}")
print(f"Records matched by rules: {matched_records:,} ({100 * matched_records / total_records:.1f}%)")
print()
print("Category breakdown (by record count):")
print(
    norm_counts.groupby("category_auto")["count"].sum()
    .sort_values(ascending=False)
    .to_string()
)
print()
print("Top 25 unmatched normalized sections by record count (prioritize these for manual labeling):")
unmatched = norm_counts[norm_counts["category_auto"].isna()].sort_values("count", ascending=False)
print(unmatched[["norm_section", "count"]].head(25).to_string(index=False))

section_counts.to_csv(LABELED_SECTIONS_PATH, index=False)
print(f"\nSaved unique-section labels to {LABELED_SECTIONS_PATH}")

# Merge labels back onto the full dataset (joined on norm_section) and discard unmatched rows
df["norm_section"] = df["CodeSection"].apply(normalize_code_section)

label_lookup = norm_counts[["norm_section", "category_auto"]]
df = df.merge(label_lookup, on="norm_section", how="left")

before_label_filter = len(df)
df = df.dropna(subset=["category_auto"])
removed_unmatched = before_label_filter - len(df)
print(f"\nRecords before dropping unmatched categories: {before_label_filter:,}")
print(f"Records after dropping unmatched categories:  {len(df):,}")
print(f"Rows discarded for unmatched category: {removed_unmatched:,} "
      f"({100 * removed_unmatched / before_label_filter:.2f}% of rows entering the labeling step)")

df.to_csv(CLEANED_DATA_PATH, index=False)
print(f"Saved final cleaned + labeled dataset to {CLEANED_DATA_PATH}")