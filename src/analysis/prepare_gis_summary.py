import pandas as pd
from pathlib import Path


# --------------------------------------------------
# 1. File paths
# --------------------------------------------------

input_file = Path("data/processed/rwanda_rainfall_cleaned.csv")
output_file = Path("data/processed/rainfall_district_summary.csv")


# --------------------------------------------------
# 2. Load cleaned rainfall data
# --------------------------------------------------

df = pd.read_csv(input_file)

df["date"] = pd.to_datetime(df["date"])

print("Cleaned rainfall dataset loaded.")
print("Rows:", len(df))


# --------------------------------------------------
# 3. Keep district-level rainfall only
# --------------------------------------------------

districts = df[df["adm_level"] == 2].copy()

print("\nDistrict-level rows:", len(districts))
print("Unique district PCODEs:", districts["PCODE"].nunique())


# --------------------------------------------------
# 4. Combine records sharing the same PCODE and date
#    using pixel-weighted rainfall values
# --------------------------------------------------

def weighted_mean(group, column):
    valid = group[[column, "n_pixels"]].dropna()

    if valid.empty:
        return pd.NA

    return (
        (valid[column] * valid["n_pixels"]).sum()
        / valid["n_pixels"].sum()
    )


district_daily = (
    districts.groupby(["PCODE", "date"], as_index=False)
    .apply(
        lambda g: pd.Series(
            {
                "rfh": weighted_mean(g, "rfh"),
                "rfh_avg": weighted_mean(g, "rfh_avg"),
                "n_pixels": g["n_pixels"].sum(),
            }
        ),
        include_groups=False,
    )
)


# --------------------------------------------------
# 5. Create one summary row per district
# --------------------------------------------------

district_summary = (
    district_daily.groupby("PCODE")
    .agg(
        observation_count=("date", "count"),
        mean_rainfall_mm=("rfh", "mean"),
        min_rainfall_mm=("rfh", "min"),
        max_rainfall_mm=("rfh", "max"),
        mean_long_term_average_mm=("rfh_avg", "mean"),
        mean_pixel_coverage=("n_pixels", "mean"),
    )
    .reset_index()
)


# --------------------------------------------------
# 6. Validate final district summary
# --------------------------------------------------

print("\nGIS-ready district summary:")
print("Rows:", len(district_summary))
print("Unique PCODEs:", district_summary["PCODE"].nunique())

if len(district_summary) != 30:
    raise ValueError(
        f"Expected 30 districts, found {len(district_summary)}."
    )

if not district_summary["PCODE"].is_unique:
    raise ValueError("PCODE must be unique.")

print("\nRW36 summary:")
print(
    district_summary[
        district_summary["PCODE"] == "RW36"
    ].to_string(index=False)
)


# --------------------------------------------------
# 7. Save GIS-ready output
# --------------------------------------------------

district_summary.to_csv(output_file, index=False)

print("\nGIS district summary created successfully.")
print("Output:", output_file)