import pandas as pd


# =========================================================
# 1. LOAD RAW DATA
# =========================================================

input_path = "data/raw/rwa-rainfall-subnat-full.csv"
output_path = "data/processed/rwanda_rainfall_cleaned.csv"

df = pd.read_csv(input_path)

print("Raw dataset loaded successfully.")
print("Raw shape:", df.shape)


# =========================================================
# 2. STANDARDIZE DATA TYPES
# =========================================================

# Convert date to datetime
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# Convert pixel count to integer
df["n_pixels"] = df["n_pixels"].astype("int64")


# =========================================================
# 3. DATE VALIDATION
# =========================================================

invalid_dates = df["date"].isna().sum()

print("\nDate validation:")
print("Invalid dates:", invalid_dates)
print("Date range:", df["date"].min(), "to", df["date"].max())


# =========================================================
# 4. IDENTIFIER VALIDATION
# =========================================================

print("\nIdentifier validation:")

print("Missing adm_id:", df["adm_id"].isna().sum())
print("Missing PCODE:", df["PCODE"].isna().sum())

whitespace_pcodes = (
    df["PCODE"].str.strip().ne(df["PCODE"]).sum()
)

print(
    "PCODEs with leading/trailing whitespace:",
    whitespace_pcodes
)


# =========================================================
# 5. ADMINISTRATIVE STRUCTURE VALIDATION
# =========================================================

print("\nAdministrative structure:")

print(
    "Unique administrative locations:",
    df["adm_id"].nunique()
)

print(
    "Unique PCODEs:",
    df["PCODE"].nunique()
)

print(
    "Administrative levels:",
    sorted(df["adm_level"].unique())
)

# Number of PCODEs at each administrative level
pcode_by_level = (
    df.groupby("adm_level")["PCODE"]
    .nunique()
)

print("\nPCODEs by administrative level:")
print(pcode_by_level)


# =========================================================
# 6. PCODE → ADM_ID CONSISTENCY
# =========================================================

pcode_location_check = (
    df.groupby("PCODE")["adm_id"]
    .nunique()
)

duplicate_pcodes = pcode_location_check[
    pcode_location_check > 1
]

print("\nPCODE-to-adm_id consistency:")
print(
    "PCODEs linked to multiple adm_id values:",
    len(duplicate_pcodes)
)

if not duplicate_pcodes.empty:

    print("\nPCODE anomalies:")
    print(duplicate_pcodes)

    # Detailed investigation
    for pcode in duplicate_pcodes.index:

        print("\n" + "=" * 60)
        print(f"Investigating PCODE: {pcode}")

        pcode_data = df[df["PCODE"] == pcode]

        print("\nAdministrative IDs:")
        print(
            pcode_data["adm_id"]
            .value_counts()
            .sort_index()
        )

        print("\nAdministrative levels:")
        print(
            pcode_data["adm_level"]
            .value_counts()
            .sort_index()
        )

        print("\nDate ranges by adm_id:")
        print(
            pcode_data
            .groupby("adm_id")["date"]
            .agg(["min", "max", "count"])
        )

        print("\nVersions by adm_id:")
        print(
            pcode_data
            .groupby(["adm_id", "version"])
            .size()
        )


# =========================================================
# 7. TIME-SERIES VALIDATION
# =========================================================

print("\nTime-series validation:")

observations_per_location = (
    df.groupby("adm_id")
    .size()
)

unique_dates_per_location = (
    df.groupby("adm_id")["date"]
    .nunique()
)

print(
    "Observation counts consistent:",
    observations_per_location.nunique() == 1
)

print(
    "Unique date counts consistent:",
    unique_dates_per_location.nunique() == 1
)


# Check that every administrative location has
# the same date sequence
dates_per_location = (
    df.groupby("adm_id")["date"]
    .apply(set)
)

reference_dates = dates_per_location.iloc[0]

inconsistent_date_sequences = dates_per_location[
    dates_per_location.apply(
        lambda dates: dates != reference_dates
    )
]

print(
    "Locations with inconsistent date sequences:",
    len(inconsistent_date_sequences)
)


# =========================================================
# 8. DUPLICATE ROW VALIDATION
# =========================================================

duplicate_rows = df.duplicated().sum()

print("\nDuplicate validation:")
print("Duplicate rows:", duplicate_rows)


# =========================================================
# 9. RAINFALL VALUE VALIDATION
# =========================================================

rainfall_columns = [
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

negative_rainfall = (
    df[rainfall_columns] < 0
).sum()

print("\nRainfall validation:")
print("Negative rainfall values:")
print(negative_rainfall)


# =========================================================
# 10. PIXEL COUNT VALIDATION
# =========================================================

invalid_pixels = (
    df["n_pixels"] <= 0
).sum()

print("\nPixel-count validation:")
print("Invalid pixel counts:", invalid_pixels)


# =========================================================
# 11. VERSION VALIDATION
# =========================================================

print("\nData versions:")
print(
    df["version"]
    .value_counts()
)

expected_versions = {
    "final",
    "prelim",
    "forecast"
}

unexpected_versions = set(
    df["version"].unique()
) - expected_versions

print(
    "Unexpected version values:",
    unexpected_versions
)


# =========================================================
# 12. MISSING-VALUE VALIDATION
# =========================================================

print("\nMissing values:")

missing_values = df.isna().sum()

print(missing_values)


# Expected structured missing values
expected_missing_columns = [
    "r1h",
    "r1h_avg",
    "r3h",
    "r3h_avg",
    "r1q",
    "r3q"
]

print("\nStructured missing-value check:")

for column in expected_missing_columns:

    missing_rows = df[df[column].isna()]

    print(
        f"{column}: {len(missing_rows)} missing"
    )

    if not missing_rows.empty:

        print(
            "  Date range:",
            missing_rows["date"].min(),
            "to",
            missing_rows["date"].max()
        )

        print(
            "  Versions:",
            missing_rows["version"]
            .value_counts()
            .to_dict()
        )


# =========================================================
# 13. CANDIDATE KEY VALIDATION
# =========================================================

key_columns = [
    "date",
    "adm_id",
    "version"
]

key_counts = (
    df.groupby(key_columns)
    .size()
)

duplicate_keys = key_counts[
    key_counts > 1
]

print("\nCandidate key validation:")

print("Total rows:", len(df))

print(
    "Unique date + adm_id + version combinations:",
    len(key_counts)
)

print(
    "Duplicate key combinations:",
    len(duplicate_keys)
)

if duplicate_keys.empty:

    print(
        "Result: date + adm_id + version "
        "uniquely identifies every row."
    )

else:

    print(
        "Result: candidate key is NOT unique."
    )

    print("\nDuplicate key combinations:")
    print(duplicate_keys)


# =========================================================
# 14. FINAL DATA QUALITY SUMMARY
# =========================================================

print("\n" + "=" * 60)
print("FINAL DATA QUALITY SUMMARY")
print("=" * 60)

print("Rows:", len(df))
print("Columns:", len(df.columns))
print("Duplicate rows:", duplicate_rows)
print("Invalid dates:", invalid_dates)
print("Missing adm_id:", df["adm_id"].isna().sum())
print("Missing PCODE:", df["PCODE"].isna().sum())
print("Invalid pixel counts:", invalid_pixels)
print(
    "PCODE → multiple adm_id anomalies:",
    len(duplicate_pcodes)
)
print(
    "Duplicate candidate keys:",
    len(duplicate_keys)
)

print("\nFinal data types:")
print(df.dtypes)


# =========================================================
# 15. SAVE PROCESSED DATASET
# =========================================================

df.to_csv(
    output_path,
    index=False
)

print("\nProcessed dataset saved successfully.")
print("Output:", output_path)