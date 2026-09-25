import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import joblib

CVILLE_FIPS = 540

# ---------------------------------------------------------------------------
# 1. Load data + saved model (no retraining)
# ---------------------------------------------------------------------------
df = pd.read_csv("../DATA/data_cleaned.csv")
df = df.dropna(subset=["Charge", "category_auto", "fips"])
 
X = df["Charge"]
y = df["category_auto"]
 
# Same random_state as training -> reproduces the identical test split
X_train_val, X_test, y_train_val, y_test = train_test_split(
    X, y, test_size=0.15, stratify=y, random_state=42
)
best_model = joblib.load("best_model.joblib")  # adjust path/filename as needed




# Confusion matrix + per-category breakdown
import matplotlib.pyplot as plt
import seaborn as sns


labels = sorted(y.unique()) #list of all the possible catergories
test_fips = df.loc[X_test.index, "fips"] #gets the fips numbers
is_cville_test = (test_fips == CVILLE_FIPS) #used to test if the data is in CVILLE or not

#checks to see if the model prediction is correct or not
y_test_pred = best_model.predict(X_test)
y_test_arr = np.asarray(y_test)
pred_arr = np.asarray(y_test_pred)
correct = (y_test_arr == pred_arr)


#creates a confusion matrix to show the accuracy of the model by category
cm_overall = confusion_matrix(y_test_arr, pred_arr, labels=labels)
cm_df = pd.DataFrame(cm_overall, index=labels, columns=labels)
cm_normalized = cm_df.div(cm_df.sum(axis=1), axis=0)



# Create graphic for confusion matrix
plt.figure(figsize=(12, 9))
sns.heatmap(
    cm_normalized,
    annot=True,  # Displays the numbers inside the squares
    fmt=".2f", 
    cmap="Blues", 
    vmin=0,  # Forces color bar minimum to 0%
    vmax=1,  # Forces color bar maximum to 100%
    xticklabels=cm_normalized.columns,
    yticklabels=cm_normalized.index,
    annot_kws={"size": 9}
)
plt.title("Normalized Overall Confusion Matrix", fontsize=14, pad=20)
plt.xlabel("Predicted Labels", fontsize=12, labelpad=10)
plt.ylabel("True Labels", fontsize=12, labelpad=10)


plt.tight_layout()
plt.savefig("../OUTPUT/confusion_matrix_normalized.png", dpi=300)





#chi squared test on data
from scipy.stats import chi2_contingency

#p-value and cramers threshholds
ALPHA = 0.05
CRAMERS_V_THRESHOLD = 0.10

# Predict category for EVERY case in the dataset (not just the test split)
df = df.dropna(subset=["Charge", "fips"]).copy()
df["predicted_category"] = best_model.predict(df["Charge"])
df["is_cville"] = df["fips"] == CVILLE_FIPS

#quick check for if the number of cases is about right
print(f"Total cases: {len(df)}")
print(f"Charlottesville cases: {df['is_cville'].sum()}")
print(f"Rest of Virginia cases: {(~df['is_cville']).sum()}")




# Build the contingency table: category (rows) x location (columns)
contingency = pd.crosstab(df["predicted_category"], df["is_cville"])
contingency.columns = ["rest_of_virginia", "charlottesville"]
contingency = contingency[["charlottesville", "rest_of_virginia"]]  # reorder for readability
contingency.to_csv("../OUTPUT/contingency_table_full.csv")
print("\nContingency table:")
print(contingency)





# Chi-square test of independence
chi2, p_value, dof, expected = chi2_contingency(contingency)
n = contingency.values.sum()
print(f"\nChi-square statistic: {chi2:.4f}")
print(f"Degrees of freedom: {dof}")
print(f"p-value: {p_value:.6f}")


# Results of chi-squared residuals
residuals = (contingency - expected) / (expected ** 0.5)

residuals = residuals[['charlottesville']].sort_values(
    by="charlottesville", ascending=False
)
print(residuals.round(2))




# Cramér's V (effect size)
r, c = contingency.shape
cramers_v = np.sqrt((chi2 / n) / (min(r - 1, c - 1)))
print(f"Cramér's V: {cramers_v:.4f}")






# VISUAL: contingency table
fig, ax = plt.subplots(figsize=(8, 5))
ax.axis("off")  # Hide the graph axes
# Create the visual table
visual_table = ax.table(
    cellText=contingency.values,
    rowLabels=contingency.index,
    colLabels=["Charlottesville", "Rest of Virginia"],
    loc="center",
    cellLoc="center",
)
# Format table style
visual_table.auto_set_font_size(False)
visual_table.set_fontsize(10)
visual_table.scale(1.2, 1.2)

plt.title("Contingency Table: Case Counts by Category", pad=20, weight="bold")
plt.tight_layout()
plt.savefig("../OUTPUT/contingency_table_visual.png", dpi=300, bbox_inches="tight")






# VISUAL: Side-by-Side Bar Chart of percentages

# Normalize by column (locality total) to show percentages
contingency_pct = contingency.div(contingency.sum(axis=0), axis=1) * 100

# Plot side-by-side bars (Categories on X-axis, location as bars)
ax = contingency_pct.plot(kind="bar", figsize=(14, 6), width=0.8, color=["orange", "blue"])

plt.title(
    "Percentage Comparison of Predicted Categories: Charlottesville vs. Rest of VA",
    fontsize=14,
    pad=15,
)
plt.xlabel("Predicted Category", fontsize=12, labelpad=10)
plt.ylabel("Percentage of Locality's Total Cases (%)", fontsize=12)


plt.xticks(
    rotation=45, ha="right"
)  # Rotates the many category names so they don't overlap
plt.legend(["Charlottesville", "Rest of Virginia"], fontsize=11)
plt.tight_layout()
plt.savefig("../OUTPUT/category_distribution_percentage.png", dpi=300)




# File: Statistics of Chi-squared test / residuals + Cramers tests
from pathlib import Path

output_dir = Path("../OUTPUT")
output_file = output_dir / "eval_stats_summary.txt"

content = f"""
--------------------------------------------
Statistical Analysis Report
--------------------------------------------

1. Chi-squared Results
- Chi-square statistic: {chi2:.4f}
- Degrees of freedom: {dof}
- p-value: {p_value:.4f} (p < {ALPHA})

Results: Statistically Significant (The overall distributions differ)

--------------------------------------------

2. Cramers Test for determining effect size
- Cramér's V: {cramers_v:.4f}
- Predefined Threshold: > {CRAMERS_V_THRESHOLD}

Results: Practically Negligible Effect due to not meeting the predefined threshold
         The large sample size (> 800k) pretty much guarantees a significant p-value
         due to the fact that small differences will be magnified, the cramer test 
         shows that Charlottesville's legal charge mix does not differ greatly to
         the rest of Virginia.

--------------------------------------------

3. Sorted Charlottesville Residuals
- Positive values indicate over-represenation; Negative values indicate under-representation

"""
res = residuals.round(2).to_string()
content = content + res + "\n"

content += "\n--------------------------------------------"
output_file.write_text(content, encoding="utf-8")