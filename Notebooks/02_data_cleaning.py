import pandas as pd

# Path to the raw rainfall dataset
file_path = "data/raw/rwa-rainfall-subnat-full.csv"

# Load the dataset
df = pd.read_csv(file_path)

print("Raw dataset loaded successfully.")
print("Shape:", df.shape)

# Convert the date column from text to datetime

df['date'] = pd.to_datetime(df['date'], errors='coerce')
# Check the date data type
print("\nDate data type:")
print(df['date'].dtype)

# Check for invalid dates
invalid_dates = df['date'].isna().sum()
print("\nNumber of invalid dates:", invalid_dates) 

# Check the date range
date_range = df['date'].min(), df['date'].max()
print("\nDate range:", date_range)

# # Investigate missing values in r1h

# Count missing r1h values
missing_r1h_count = df["r1h"].isna().sum()

print("\nMissing r1h values:", missing_r1h_count)

# Extract rows where r1h is missing
missing_r1h_rows = df.loc[df["r1h"].isna()]

# Count missing r1h values by date
missing_r1h_by_date = (
    missing_r1h_rows["date"]
    .value_counts()
    .sort_index()
)

print("\nMissing r1h values by date:")
print(missing_r1h_by_date)

# Identify locations affected by missing r1h values
missing_r1h_locations = (
    missing_r1h_rows[["date", "adm_id", "PCODE"]]
    .sort_values(["date", "adm_id"])
)

print("\nLocations with missing r1h values:")
print(missing_r1h_locations.to_string(index=False))

# Investigate missing values in r1h_avg
missing_r1h_avg_count = df["r1h_avg"].isna().sum()

print("\nMissing r1h_avg values:", missing_r1h_avg_count)

missing_r1h_avg_rows = df.loc[df["r1h_avg"].isna()]

missing_r1h_avg_by_date = (
    missing_r1h_avg_rows["date"]
    .value_counts()
    .sort_index()
)

print("\nMissing r1h_avg values by date:")
print(missing_r1h_avg_by_date)

# Investigate missing values in r3h

missing_r3h_count = df["r3h"].isna().sum()

print("\nMissing r3h values:", missing_r3h_count)

missing_r3h_rows = df.loc[df["r3h"].isna()]

missing_r3h_by_date = (
    missing_r3h_rows["date"]
    .value_counts()
    .sort_index()
)

print("\nMissing r3h values by date:")
print(missing_r3h_by_date)

# Investigate missing values in r3h_avg

missing_r3h_avg_count = df["r3h_avg"].isna().sum()

print("\nMissing r3h_avg values:", missing_r3h_avg_count)

missing_r3h_avg_rows = df.loc[df["r3h_avg"].isna()]

missing_r3h_avg_by_date = (
    missing_r3h_avg_rows["date"]
    .value_counts()
    .sort_index()
)

print("\nMissing r3h_avg values by date:")
print(missing_r3h_avg_by_date)

# Investigate missing values in r1q

missing_r1q_count = df["r1q"].isna().sum()

print("\nMissing r1q values:", missing_r1q_count)

missing_r1q_rows = df.loc[df["r1q"].isna()]

missing_r1q_by_date = (
    missing_r1q_rows["date"]
    .value_counts()
    .sort_index()
)

print("\nMissing r1q values by date:")
print(missing_r1q_by_date)

# Investigate missing values in r3q

missing_r3q_count = df["r3q"].isna().sum()

print("\nMissing r3q values:", missing_r3q_count)

missing_r3q_rows = df.loc[df["r3q"].isna()]

missing_r3q_by_date = (
    missing_r3q_rows["date"]
    .value_counts()
    .sort_index()
)

print("\nMissing r3q values by date:")
print(missing_r3q_by_date)

# Check missing values across all columns

print("\nMissing values in all columns:")
print(df.isna().sum())

# Check the total number of records for each date
date_counts = df["date"].value_counts().sort_index()

print("\nNumber of records per date:")
print(date_counts.head(15))

# Check how many unique locations are in the dataset
print("\nNumber of unique locations:")
print(df["adm_id"].nunique())

# Check how many unique PCODEs are in the dataset
print("\nNumber of unique PCODEs:")
print(df["PCODE"].nunique())

# Investigate PCODE consistency

print("\nPCODE frequency:")
print(df["PCODE"].value_counts().sort_index())

# Find PCODEs associated with more than one adm_id
pcode_location_check = (
    df.groupby("PCODE")["adm_id"]
    .nunique()
    .sort_values(ascending=False)
)

print("\nNumber of unique adm_id values for each PCODE:")
print(pcode_location_check)

# Show PCODEs linked to multiple locations
duplicate_pcodes = pcode_location_check[pcode_location_check > 1]

print("\nPCODEs linked to multiple adm_id values:")
print(duplicate_pcodes)

# Display the affected records
if not duplicate_pcodes.empty:
    affected_pcodes = duplicate_pcodes.index

    print("\nAffected PCODE records:")
    print(
        df[df["PCODE"].isin(affected_pcodes)][
            ["adm_id", "PCODE"]
        ].drop_duplicates()
        .sort_values(["PCODE", "adm_id"])
        .to_string(index=False)
    )
    # Investigate the two locations sharing PCODE RW36

rw36_locations = (
    df[df["PCODE"] == "RW36"]
    [["adm_id", "PCODE", "adm_level", "n_pixels", "version"]]
    .drop_duplicates()
    .sort_values("adm_id")
)

print("\nDetails of locations with PCODE RW36:")
print(rw36_locations.to_string(index=False))

# Compare missing periods with the rainfall variables that are available

missing_periods = df[
    df["r1h"].isna() | df["r3h"].isna()
].copy()

print("\nRainfall values during periods with missing r1h or r3h:")
print(
    missing_periods[
        [
            "date",
            "adm_id",
            "PCODE",
            "rfh",
            "rfh_avg",
            "r1h",
            "r1h_avg",
            "r3h",
            "r3h_avg",
            "rfq",
            "r1q",
            "r3q"
        ]
    ].head(20).to_string(index=False)
)

# Missing-value summary

missing_summary = df.isna().sum()

missing_percentage = (
    df.isna().sum() / len(df) * 100
)

missing_report = pd.DataFrame({
    "missing_count": missing_summary,
    "missing_percentage": missing_percentage.round(2)
})

print("\nMissing-value summary:")
print(
    missing_report[
        missing_report["missing_count"] > 0
    ]
)

# Check the first date for each administrative location
first_dates_by_location = (
    df.groupby("adm_id")["date"]
    .min()
    .sort_index()
)

print(first_dates_by_location)

# Check missing values in the early period
early_period = df[df["date"] <= "1981-03-11"]

print(
    early_period[
        ["r1h", "r1h_avg", "r3h", "r3h_avg", "r1q", "r3q"]
    ].isna().sum()
)
# Retain structured missing values without imputation

# Check for negative rainfall values
rainfall_columns = [
    "rfh", "rfh_avg", "r1h", "r1h_avg",
    "r3h", "r3h_avg", "rfq", "r1q", "r3q"
]

negative_rainfall = (df[rainfall_columns] < 0).sum()

print("\nNegative rainfall values:")
print(negative_rainfall)

# Check for invalid pixel counts
print("\nInvalid n_pixels values:")
print((df["n_pixels"] <= 0).sum())

# Check administrative level values
print("\nUnique adm_level values:")
print(df["adm_level"].unique())

# Check the number of observations for each location
observations_per_location = df.groupby("adm_id").size()

print("\nObservations per location:")
print(observations_per_location)

# Check the number of unique dates for each location
unique_dates_per_location = df.groupby("adm_id")["date"].nunique()

print("\nUnique dates per location:")
print(unique_dates_per_location)

# Check whether dates follow the expected dekadal sequence
expected_dates = pd.date_range(
    start=df["date"].min(),
    end=df["date"].max(),
    freq="10D"
)

actual_dates = pd.Series(df["date"].unique()).sort_values()

print("\nExpected number of dates:", len(expected_dates))
print("Actual number of dates:", len(actual_dates))

missing_dates = expected_dates.difference(actual_dates)

print("\nMissing dates:")
print(missing_dates)

# Check whether all locations have the same rainfall dates
dates_per_location = df.groupby("adm_id")["date"].apply(set)

reference_dates = dates_per_location.iloc[0]

inconsistent_locations = dates_per_location[
    dates_per_location.apply(lambda x: x != reference_dates)
]

print("\nLocations with inconsistent date sequences:")
print(inconsistent_locations)
# Check the available rainfall data versions
print("\nVersion values:")
print(df["version"].value_counts())
# Retain the original version categories

# Check for whitespace in administrative identifiers
pcode_whitespace = df["PCODE"].str.strip().ne(df["PCODE"]).sum()

print("\nPCODE values with leading or trailing whitespace:", pcode_whitespace)

# Check administrative ID validity
print("\nMissing adm_id values:", df["adm_id"].isna().sum())
print("adm_id data type:", df["adm_id"].dtype)

# Check for missing PCODE values
print("\nMissing PCODE values:", df["PCODE"].isna().sum())

# Check data types before final cleaning
print("\nData types before cleaning:")
print(df.dtypes)

# Check whether pixel counts are whole numbers
print("\nNon-integer n_pixels values:")
print(df.loc[df["n_pixels"] % 1 != 0, "n_pixels"])

# Convert pixel counts from float to integer
df["n_pixels"] = df["n_pixels"].astype("int64")

# Verify the cleaned data type
print("\nn_pixels data type after cleaning:")
print(df["n_pixels"].dtype)

# Save the cleaned dataset
output_path = "data/processed/rwanda_rainfall_cleaned.csv"

df.to_csv(output_path, index=False)

print("\nCleaned dataset saved successfully.")
print("Saved to:", output_path)

# Validate the cleaned dataset
print("\nCleaned dataset shape:")
print(df.shape)

print("\nCleaned dataset columns:")
print(df.columns.tolist())

print("\nMissing values after cleaning:")
print(df.isna().sum())

print("\nData types after cleaning:")
print(df.dtypes)

print("\nDuplicate rows after cleaning:")
print(df.duplicated().sum())