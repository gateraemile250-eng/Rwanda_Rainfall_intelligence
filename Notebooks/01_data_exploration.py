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


