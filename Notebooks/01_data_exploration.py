import pandas as pd
from pathlib import Path


# Find the project root directory
project_root = Path(__file__).resolve().parents[1]

# Path to the raw rainfall dataset
data_path = project_root / "data" / "raw" / "rwa-rainfall-subnat-full.csv"

# Load the dataset
df = pd.read_csv(data_path)


# Display basic information about the dataset
print("Dataset shape:")
print(df.shape)

print("\nColumn names:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isna().sum())

print("\nDuplicate rows:")
print(df.duplicated().sum())

# Inspect Level-2 administrative units

print("\nUnique values in each object/string column:")

for column in df.select_dtypes(include="object").columns:
    print(f"\n{column}:")
    print("Number of unique values:", df[column].nunique())
    print(df[column].dropna().unique())

    # Inspect administrative levels and their PCODEs

print("\nAdministrative levels and PCODEs:")

adm_summary = (
    df.groupby("adm_level")["PCODE"]
    .nunique()
    .reset_index(name="number_of_pcodes")
)

print(adm_summary)

print("\nPCODEs by administrative level:")

for level in sorted(df["adm_level"].unique()):
    pcodes = sorted(df.loc[df["adm_level"] == level, "PCODE"].unique())

    print(f"\nADM Level {level} ({len(pcodes)} PCODEs):")
    print(pcodes)


