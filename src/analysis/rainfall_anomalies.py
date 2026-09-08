"""
Analyze rainfall anomalies and deficits across Rwanda.

This module calculates annual rainfall indicators, historical
rainfall baselines, rainfall anomalies, wet/dry classifications,
and saves the results as a processed analytical dataset.
"""

import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine


def load_rainfall_data():
    """
    Load final rainfall observations from PostgreSQL.

    Returns:
        pandas.DataFrame: Final rainfall observations.
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


def prepare_annual_rainfall(df):
    """
    Calculate annual rainfall for each administrative location.

    Only complete years with 36 observations per location
    are retained.

    Returns:
        pandas.DataFrame: Annual rainfall by location and year.
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
            observation_count=("rfh", "count")
        )
    )

    # Identify years where every location has 36 observations.
    complete_years = (
        annual_rainfall
        .groupby("year")["observation_count"]
        .min()
    )

    complete_years = complete_years[
        complete_years == 36
    ].index

    annual_rainfall = annual_rainfall[
        annual_rainfall["year"].isin(complete_years)
    ]

    return annual_rainfall


def calculate_yearly_rainfall(annual_rainfall):
    """
    Calculate the average annual rainfall across all locations
    for each year.

    Returns:
        pandas.DataFrame: Year-level rainfall statistics.
    """

    yearly_rainfall = (
        annual_rainfall
        .groupby("year", as_index=False)
        .agg(
            mean_annual_rainfall_mm=("annual_rainfall_mm", "mean"),
            location_count=("adm_id", "nunique")
        )
    )

    return yearly_rainfall


def calculate_rwanda_baseline(yearly_rainfall):
    """
    Calculate the historical Rwanda-wide annual rainfall baseline.

    The baseline is the average of the yearly rainfall indicators
    across all complete years in the analysis period.

    Returns:
        float: Historical Rwanda-wide annual rainfall baseline in mm.
    """

    baseline = (
        yearly_rainfall["mean_annual_rainfall_mm"]
        .mean()
    )

    return baseline


def calculate_yearly_anomalies(
    yearly_rainfall,
    rwanda_baseline
):
    """
    Calculate annual rainfall anomalies relative to the
    historical Rwanda-wide baseline.

    Anomaly in mm:
        Annual rainfall - historical baseline

    Anomaly percentage:
        (Anomaly / historical baseline) * 100

    Returns:
        pandas.DataFrame: Yearly rainfall anomalies.
    """

    yearly_anomalies = yearly_rainfall.copy()

    yearly_anomalies["anomaly_mm"] = (
        yearly_anomalies["mean_annual_rainfall_mm"]
        - rwanda_baseline
    )

    yearly_anomalies["anomaly_percent"] = (
        yearly_anomalies["anomaly_mm"]
        / rwanda_baseline
        * 100
    )

    # Classify years based on their anomaly.
    yearly_anomalies["rainfall_class"] = pd.cut(
        yearly_anomalies["anomaly_percent"],
        bins=[
            float("-inf"),
            -10,
            10,
            float("inf")
        ],
        labels=[
            "Dry",
            "Near Normal",
            "Wet"
        ]
    )

    return yearly_anomalies


def calculate_location_baseline(annual_rainfall):
    """
    Calculate the long-term annual rainfall baseline for each location.

    Returns:
        pandas.DataFrame: Historical rainfall baseline by location.
    """

    location_baseline = (
        annual_rainfall
        .groupby(
            ["adm_level", "adm_id", "pcode"],
            as_index=False
        )
        .agg(
            baseline_rainfall_mm=("annual_rainfall_mm", "mean"),
            baseline_std_mm=("annual_rainfall_mm", "std"),
            years_analyzed=("annual_rainfall_mm", "count")
        )
    )

    return location_baseline


def save_yearly_anomalies(yearly_anomalies):
    """
    Save yearly rainfall anomaly results as a processed CSV file.

    Parameters:
        yearly_anomalies (pandas.DataFrame): Yearly rainfall
        anomaly dataset.

    Returns:
        None
    """

    output_path = "data/processed/rainfall_yearly_anomalies.csv"

    yearly_anomalies.to_csv(
        output_path,
        index=False
    )

    print(
        f"\nYearly anomaly dataset saved to: "
        f"{output_path}"
    )


if __name__ == "__main__":

    print("=" * 60)
    print("RWANDA RAINFALL ANOMALY ANALYSIS")
    print("=" * 60)

    print("\n[1/6] Loading rainfall data...")

    df = load_rainfall_data()

    print(
        f"Loaded {len(df):,} final rainfall observations."
    )

    print("\n[2/6] Calculating annual rainfall...")

    annual_rainfall = prepare_annual_rainfall(df)

    print(
        f"Annual rainfall calculated for "
        f"{len(annual_rainfall):,} location-year records."
    )

    print("\n[3/6] Calculating yearly rainfall indicator...")

    yearly_rainfall = calculate_yearly_rainfall(
        annual_rainfall
    )

    print(
        f"Yearly rainfall calculated for "
        f"{len(yearly_rainfall):,} years."
    )

    print("\nCalculating Rwanda-wide historical baseline...")

    rwanda_baseline = calculate_rwanda_baseline(
        yearly_rainfall
    )

    print(
        f"Historical Rwanda-wide baseline: "
        f"{rwanda_baseline:.2f} mm/year"
    )

    print("\n[4/6] Calculating yearly rainfall anomalies...")

    yearly_anomalies = calculate_yearly_anomalies(
        yearly_rainfall,
        rwanda_baseline
    )

    print("\nYearly rainfall anomalies:")

    print(
        yearly_anomalies[
            [
                "year",
                "mean_annual_rainfall_mm",
                "anomaly_mm",
                "anomaly_percent",
                "rainfall_class"
            ]
        ]
        .to_string(index=False)
    )

    print("\nDriest years:")

    print(
        yearly_anomalies
        .sort_values("anomaly_mm")
        [
            [
                "year",
                "mean_annual_rainfall_mm",
                "anomaly_mm",
                "anomaly_percent",
                "rainfall_class"
            ]
        ]
        .head(5)
        .to_string(index=False)
    )

    print("\nWettest years:")

    print(
        yearly_anomalies
        .sort_values(
            "anomaly_mm",
            ascending=False
        )
        [
            [
                "year",
                "mean_annual_rainfall_mm",
                "anomaly_mm",
                "anomaly_percent",
                "rainfall_class"
            ]
        ]
        .head(5)
        .to_string(index=False)
    )

    print("\n2000 rainfall anomaly:")

    year_2000 = yearly_anomalies[
        yearly_anomalies["year"] == 2000
    ]

    print(
        year_2000[
            [
                "year",
                "mean_annual_rainfall_mm",
                "anomaly_mm",
                "anomaly_percent",
                "rainfall_class"
            ]
        ]
        .to_string(index=False)
    )

    print("\n[5/6] Saving yearly anomaly dataset...")

    save_yearly_anomalies(
        yearly_anomalies
    )

    print("\n[6/6] Calculating location baselines...")

    location_baseline = calculate_location_baseline(
        annual_rainfall
    )

    print(
        f"Historical baselines calculated for "
        f"{len(location_baseline):,} locations."
    )

    print("\nLocation rainfall baselines:")

    print(
        location_baseline
        .sort_values(
            "baseline_rainfall_mm",
            ascending=False
        )
        .to_string(index=False)
    )

    print("\n" + "=" * 60)
    print("RAINFALL ANOMALY ANALYSIS COMPLETED SUCCESSFULLY")
    print("=" * 60)