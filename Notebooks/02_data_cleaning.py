import pandas as pd


# Load the raw rainfall dataset
input_path = "data/raw/rwa-rainfall-subnat-full.csv"
df = pd.read_csv(input_path)

print("Raw dataset loaded successfully.")
print("Raw shape:", df.shape)


# Convert the date column to datetime
df["date"] = pd.to_datetime(df["date"], errors="coerce")


# Validate the date column
invalid_dates = df["date"].isna().sum()

print("\nDate validation:")
print("Invalid dates:", invalid_dates)
print("Date range:", df["date"].min(), "to", df["date"].max())


# Validate administrative identifiers
print("\nIdentifier validation:")
print("Missing adm_id:", df["adm_id"].isna().sum())
print("Missing PCODE:", df["PCODE"].isna().sum())
print(
    "PCODE values with leading/trailing whitespace:",
    df["PCODE"].str.strip().ne(df["PCODE"]).sum()
)


# Validate the administrative structure
print("\nAdministrative structure:")
print("Unique administrative locations:", df["adm_id"].nunique())
print("Unique PCODEs:", df["PCODE"].nunique())
print("Administrative levels:", sorted(df["adm_level"].unique()))


# Check whether each PCODE maps to a single administrative location
pcode_location_check = (
    df.groupby("PCODE")["adm_id"]
    .nunique()
)

duplicate_pcodes = pcode_location_check[
    pcode_location_check > 1
]

print("\nPCODE-to-location consistency:")
print("PCODEs linked to multiple adm_id values:", len(duplicate_pcodes))

if not duplicate_pcodes.empty:
    print(duplicate_pcodes)


# Validate time-series consistency across locations
observations_per_location = df.groupby("adm_id").size()
unique_dates_per_location = df.groupby("adm_id")["date"].nunique()

print("\nTime-series validation:")
print(
    "Observation counts consistent:",
    observations_per_location.nunique() == 1
)
print(
    "Unique date counts consistent:",
    unique_dates_per_location.nunique() == 1
)


# Confirm that all locations share the same dates
dates_per_location = df.groupby("adm_id")["date"].apply(set)
reference_dates = dates_per_location.iloc[0]

inconsistent_date_sequences = dates_per_location[
    dates_per_location.apply(lambda dates: dates != reference_dates)
]

print(
    "Locations with inconsistent date sequences:",
    len(inconsistent_date_sequences)
)


# Validate rainfall values
rainfall_columns = [
    "rfh",
    "rfh_avg",
    "r1h",
    "r1h_avg",
    "r3h",
    "r3h_avg",
    "rfq",
    "r1q",
    "r3q",
]

negative_rainfall = (df[rainfall_columns] < 0).sum()

print("\nRainfall validation:")
print("Negative rainfall values:")
print(negative_rainfall)


# Validate pixel counts
invalid_pixels = (df["n_pixels"] <= 0).sum()
non_integer_pixels = (df["n_pixels"] % 1 != 0).sum()

print("\nPixel-count validation:")
print("Invalid pixel counts:", invalid_pixels)
print("Non-integer pixel counts:", non_integer_pixels)


# Check available data versions
print("\nData versions:")
print(df["version"].value_counts())


# Retain structured missing values without imputation
#
# Missing values occur systematically at the beginning of the time series
# across derived rainfall variables. They are retained as NaN because
# replacing them with zero or estimated values could introduce false data.


# Convert pixel counts from float to integer
df["n_pixels"] = df["n_pixels"].astype("int64")


# Final validation after cleaning
print("\nFinal validation:")
print("Shape:", df.shape)
print("Duplicate rows:", df.duplicated().sum())

print("\nMissing values:")
print(df.isna().sum())

print("\nData types:")
print(df.dtypes)


# Save the cleaned dataset
output_path = "data/processed/rwanda_rainfall_cleaned.csv"

df.to_csv(output_path, index=False)

print("\nCleaned dataset saved successfully.")
print("Output:", output_path)

# ---------------------------------------------------------
# Check whether date + adm_id + version uniquely identifies
# each rainfall observation
# ---------------------------------------------------------

key_columns = ["date", "adm_id", "version"]

# Count how many rows have each combination
key_counts = df.groupby(key_columns).size()

# Find combinations that appear more than once
duplicate_keys = key_counts[key_counts > 1]

print("\nCandidate key check:")
print(f"Total rows: {len(df)}")
print(f"Unique date + adm_id + version combinations: {len(key_counts)}")
print(f"Duplicate key combinations: {len(duplicate_keys)}")

if len(duplicate_keys) == 0:
    print("Result: date + adm_id + version uniquely identifies every row.")
else:
    print("Result: date + adm_id + version is NOT unique.")
    print("\nDuplicate combinations:")
    print(duplicate_keys)