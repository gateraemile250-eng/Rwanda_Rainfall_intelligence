"""
Analyze annual rainfall patterns by administrative location in Rwanda.

This module calculates annual rainfall statistics for each location
using complete final historical observations only.
"""

import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine


def load_rainfall_data():
    """
    Load final rainfall observations from PostgreSQL.

    Returns:
        pandas.DataFrame: Historical final rainfall observations.
    """

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
            version
        FROM rainfall_observations
        WHERE version = 'final'
        ORDER BY date, adm_id;
    """

    df = pd.read_sql(query, engine)

    return df


def calculate_annual_rainfall(df):
    """
    Calculate annual rainfall statistics for each location.

    Parameters:
        df (pandas.DataFrame): Historical rainfall observations.

    Returns:
        pandas.DataFrame: Annual rainfall statistics by location.
    """

    df = df.copy()

    df["date"] = pd.to_datetime(df["date"])

    df["year"] = df["date"].dt.year

    annual_rainfall = (
        df.groupby(
            ["year", "adm_level", "adm_id", "pcode"],
            as_index=False
        )
        .agg(
            annual_rainfall_mm=("rfh", "sum"),
            mean_rainfall_mm=("rfh", "mean"),
            min_rainfall_mm=("rfh", "min"),
            max_rainfall_mm=("rfh", "max"),
            rainfall_std_mm=("rfh", "std"),
            observation_count=("rfh", "count"),
        )
    )

    return annual_rainfall


def main():
    """
    Run the location-level annual rainfall analysis.
    """

    print("=" * 60)
    print("RWANDA ANNUAL RAINFALL BY LOCATION")
    print("=" * 60)

    print("\n[1/4] Loading historical rainfall data...")

    df = load_rainfall_data()

    print(
        f"Loaded {len(df):,} final rainfall observations."
    )

    print("\n[2/4] Calculating annual rainfall by location...")

    annual_rainfall = calculate_annual_rainfall(df)

    print(
        f"Annual statistics calculated for "
        f"{len(annual_rainfall):,} location-year combinations."
    )

    print("\n[3/4] Removing incomplete years...")

    latest_complete_year = annual_rainfall["year"].max() - 1

    annual_rainfall = annual_rainfall[
        annual_rainfall["year"] <= latest_complete_year
    ].copy()

    print(
        f"Analysis uses complete years through "
        f"{latest_complete_year}."
    )

    print("\n[4/4] Inspecting annual rainfall patterns...")

    print("\nSample annual rainfall records:")

    print(
        annual_rainfall[
            [
                "year",
                "adm_level",
                "adm_id",
                "pcode",
                "annual_rainfall_mm",
                "mean_rainfall_mm",
                "rainfall_std_mm",
                "observation_count",
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

    print("\nOverall location-level statistics:")

    print(
        f"Location-year records: "
        f"{len(annual_rainfall):,}"
    )

    print(
        f"Administrative locations: "
        f"{annual_rainfall['adm_id'].nunique():,}"
    )

    print(
        f"Years analyzed: "
        f"{annual_rainfall['year'].nunique():,}"
    )

    wettest_location_year = annual_rainfall.loc[
        annual_rainfall["annual_rainfall_mm"].idxmax()
    ]

    driest_location_year = annual_rainfall.loc[
        annual_rainfall["annual_rainfall_mm"].idxmin()
    ]

    print("\nRainfall extremes across location-year records:")

    print(
        f"Wettest location-year: "
        f"{wettest_location_year['pcode']} "
        f"in {int(wettest_location_year['year'])} "
        f"({wettest_location_year['annual_rainfall_mm']:.2f} mm)"
    )

    print(
        f"Driest location-year: "
        f"{driest_location_year['pcode']} "
        f"in {int(driest_location_year['year'])} "
        f"({driest_location_year['annual_rainfall_mm']:.2f} mm)"
    )

    print("\nLocation-level annual rainfall analysis completed successfully.")


if __name__ == "__main__":
    main()