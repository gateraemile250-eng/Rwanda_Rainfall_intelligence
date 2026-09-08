"""
Spatial rainfall analysis for Rwanda.

Creates a location-level rainfall summary that will later
support GIS and PostGIS spatial analysis.
"""

import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine


def load_rainfall_data():
    """Load final rainfall observations from PostgreSQL."""

    load_dotenv()

    engine = create_engine(
        "postgresql+psycopg://",
        connect_args={
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT"),
            "dbname": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
        },
    )

    query = """
        SELECT
            date,
            adm_level,
            adm_id,
            pcode,
            rfh,
            rfh_avg
        FROM rainfall_observations
        WHERE version = 'final'
        ORDER BY date, adm_id;
    """

    return pd.read_sql(query, engine)


def calculate_spatial_summary(df):
    """
    Create one rainfall summary record for each
    administrative location.
    """

    p95 = df["rfh"].quantile(0.95)
    p99 = df["rfh"].quantile(0.99)

    summary = (
        df.groupby(
            ["adm_level", "adm_id", "pcode"],
            as_index=False
        )
        .agg(
            observation_count=("rfh", "count"),
            mean_rainfall_mm=("rfh", "mean"),
            min_rainfall_mm=("rfh", "min"),
            max_rainfall_mm=("rfh", "max"),
            rainfall_std_mm=("rfh", "std"),
            mean_long_term_average_mm=("rfh_avg", "mean"),
            extreme_95_count=(
                "rfh",
                lambda x: (x >= p95).sum()
            ),
            extreme_99_count=(
                "rfh",
                lambda x: (x >= p99).sum()
            ),
        )
    )

    summary["coefficient_of_variation"] = (
        summary["rainfall_std_mm"]
        / summary["mean_rainfall_mm"]
    )

    summary["extreme_95_percent"] = (
        summary["extreme_95_count"]
        / summary["observation_count"]
        * 100
    )

    summary["extreme_99_percent"] = (
        summary["extreme_99_count"]
        / summary["observation_count"]
        * 100
    )

    return summary.sort_values(
        ["adm_level", "mean_rainfall_mm"],
        ascending=[True, False]
    ).reset_index(drop=True)


def save_spatial_summary(summary):
    """Save the spatial rainfall summary."""

    path = "data/processed/rainfall_spatial_summary.csv"

    summary.to_csv(path, index=False)

    print(f"\nSpatial summary saved to: {path}")


if __name__ == "__main__":

    print("=" * 60)
    print("RWANDA SPATIAL RAINFALL ANALYSIS")
    print("=" * 60)

    # 1. Load data
    print("\n[1/3] Loading rainfall data...")

    df = load_rainfall_data()

    print(f"Loaded {len(df):,} final observations.")

    # 2. Calculate spatial summary
    print("\n[2/3] Calculating location-level rainfall summary...")

    spatial_summary = calculate_spatial_summary(df)

    print(
        f"Administrative locations analyzed: "
        f"{len(spatial_summary):,}"
    )

    print("\nTop locations by mean rainfall:")

    print(
        spatial_summary[
            [
                "adm_level",
                "adm_id",
                "pcode",
                "mean_rainfall_mm",
                "coefficient_of_variation",
                "extreme_99_percent",
                "max_rainfall_mm",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    # 3. Save result
    print("\n[3/3] Saving spatial dataset...")

    save_spatial_summary(spatial_summary)

    print("\n" + "=" * 60)
    print("SPATIAL RAINFALL ANALYSIS COMPLETED SUCCESSFULLY")
    print("=" * 60)