"""
Analyze the seasonal rainfall pattern in Rwanda.

This module calculates average rainfall by month using final
historical rainfall observations only.
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


def calculate_monthly_rainfall(df):
    """
    Calculate average rainfall for each calendar month.

    Parameters:
        df (pandas.DataFrame): Historical rainfall observations.

    Returns:
        pandas.DataFrame: Monthly rainfall statistics.
    """

    df = df.copy()

    df["date"] = pd.to_datetime(df["date"])

    df["month"] = df["date"].dt.month

    monthly_rainfall = (
        df.groupby("month", as_index=False)
        .agg(
            mean_rainfall_mm=("rfh", "mean"),
            min_rainfall_mm=("rfh", "min"),
            max_rainfall_mm=("rfh", "max"),
            rainfall_std_mm=("rfh", "std"),
            observation_count=("rfh", "count"),
        )
    )

    monthly_rainfall["month_name"] = pd.to_datetime(
        monthly_rainfall["month"],
        format="%m"
    ).dt.month_name()

    monthly_rainfall = monthly_rainfall.sort_values("month")

    return monthly_rainfall


def main():
    """
    Run the rainfall seasonality analysis.
    """

    print("=" * 60)
    print("RWANDA RAINFALL SEASONALITY ANALYSIS")
    print("=" * 60)

    print("\n[1/2] Loading historical rainfall data...")

    df = load_rainfall_data()

    print(
        f"Loaded {len(df):,} final rainfall observations."
    )

    print("\n[2/2] Calculating monthly rainfall patterns...")

    monthly_rainfall = calculate_monthly_rainfall(df)

    print("\nMonthly rainfall statistics:")

    print(
        monthly_rainfall[
            [
                "month_name",
                "mean_rainfall_mm",
                "min_rainfall_mm",
                "max_rainfall_mm",
                "rainfall_std_mm",
                "observation_count",
            ]
        ]
        .to_string(index=False)
    )

    wettest_month = monthly_rainfall.loc[
        monthly_rainfall["mean_rainfall_mm"].idxmax()
    ]

    driest_month = monthly_rainfall.loc[
        monthly_rainfall["mean_rainfall_mm"].idxmin()
    ]

    print("\nSeasonality summary:")

    print(
        f"Wettest month: "
        f"{wettest_month['month_name']} "
        f"({wettest_month['mean_rainfall_mm']:.2f} mm)"
    )

    print(
        f"Driest month: "
        f"{driest_month['month_name']} "
        f"({driest_month['mean_rainfall_mm']:.2f} mm)"
    )

    print("\nSeasonality analysis completed successfully.")


if __name__ == "__main__":
    main()