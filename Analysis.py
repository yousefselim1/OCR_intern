# Analysis.py
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime


file_path = "Updated Data.xlsx"   
df = pd.read_excel(file_path)


DOB_COL = "Birth date"
GENDER_COL = "Gender"


current_year = datetime.now().year


birth_years = pd.to_numeric(df[DOB_COL], errors="coerce")
ages = current_year - birth_years
ages = ages[(ages >= 0) & (ages <= 100)]   


df["AgeYears"] = ages

# Drop rows with missing gender or age 
df = df.dropna(subset=["AgeYears", GENDER_COL])

#   statistics 
print("\n Overall Age Summary:\n", df["AgeYears"].describe())

# Grouped by gender
summary_by_gender = df.groupby(GENDER_COL)["AgeYears"].describe()
print("\n Per-Gender Age Summary:\n", summary_by_gender)

#  outputs
os.makedirs("outputs", exist_ok=True)
summary_by_gender.to_csv("outputs/age_summary_by_gender.csv")

# Visualizations 

# Histogram
plt.figure(figsize=(8,5))
plt.hist(df["AgeYears"], bins=20, edgecolor="black")
plt.title("Age Distribution (Histogram)")
plt.xlabel("Age (years)")
plt.ylabel("Frequency")
plt.savefig("outputs/age_histogram.png")
plt.show()

# Boxplot by gender
plt.figure(figsize=(8,6))
df.boxplot(column="AgeYears", by=GENDER_COL, grid=False)
plt.title("Age Distribution by Gender")
plt.suptitle("")
plt.xlabel("Gender")
plt.ylabel("Age (years)")
plt.savefig("outputs/age_boxplot_by_gender.png")
plt.show()

# ECDF with Median & Quartiles 
a = np.sort(df["AgeYears"].dropna())
y = np.arange(1, len(a)+1) / len(a)

plt.figure(figsize=(8,5))
plt.plot(a, y, drawstyle="steps-post", label="ECDF")

#  percentiles
median = np.median(a)
q25 = np.percentile(a, 25)
q75 = np.percentile(a, 75)

# Add vertical lines
plt.axvline(median, color="red", linestyle=":", label=f"Median = {median:.1f}")
plt.axvline(q25, color="green", linestyle="--", label=f"25% = {q25:.1f}")
plt.axvline(q75, color="blue", linestyle="-.", label=f"75% = {q75:.1f}")

plt.title("Age Distribution (ECDF)")
plt.xlabel("Age (years)")
plt.ylabel("Proportion ≤ Age")
plt.grid(True, linestyle="-.", alpha=0.7)
plt.legend()
plt.savefig("outputs/age_ecdf.png")
plt.show()

print("\n All plots saved in 'outputs/' folder.")
