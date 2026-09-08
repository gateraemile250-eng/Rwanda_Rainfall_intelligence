"""
Analyze the historical rainfall baseline for Rwanda.

This module calculates long-term rainfall statistics for each
administrative location using final rainfall observations only.
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
            rfh_avg,
            version
        FROM rainfall_observations
        WHERE version = 'final'
        ORDER BY date, adm_id;
    """

    df = pd.read_sql(query, engine)

    return df


def calculate_baseline(df):
    """
    Calculate long-term rainfall baseline statistics by location.

    Parameters:
        df (pandas.DataFrame): Historical rainfall observations.

    Returns:
        pandas.DataFrame: Rainfall baseline statistics by location.
    """

    baseline = (
        df.groupby(
            ["adm_level", "adm_id", "pcode"],
            as_index=False
        )
        .agg(
            mean_rainfall_mm=("rfh", "mean"),
            min_rainfall_mm=("rfh", "min"),
            max_rainfall_mm=("rfh", "max"),
            rainfall_std_mm=("rfh", "std"),
            mean_long_term_average_mm=("rfh_avg", "mean"),
            observation_count=("rfh", "count"),
        )
    )

    baseline["coefficient_of_variation"] = (
        baseline["rainfall_std_mm"]
        / baseline["mean_rainfall_mm"]
    )

    baseline = baseline.sort_values(
        "mean_rainfall_mm",
        ascending=False
    )

    return baseline


def main():
    """
    Run the rainfall baseline analysis.
    """

    print("=" * 60)
    print("RWANDA RAINFALL BASELINE ANALYSIS")
    print("=" * 60)

    print("\n[1/2] Loading historical rainfall data...")

    df = load_rainfall_data()

    print(
        f"Loaded {len(df):,} final rainfall observations."
    )

    print("\n[2/2] Calculating rainfall baseline...")

    baseline = calculate_baseline(df)

    print(
        f"Baseline calculated for "
        f"{len(baseline):,} administrative locations."
    )

    print("\nTop locations by mean rainfall:")

    print(
        baseline[
            [
                "adm_level",
                "adm_id",
                "pcode",
                "mean_rainfall_mm",
                "rainfall_std_mm",
                "coefficient_of_variation",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    print("\nOverall rainfall statistics:")

    print(
        f"Mean rainfall: "
        f"{df['rfh'].mean():.2f} mm"
    )

    print(
        f"Minimum rainfall: "
        f"{df['rfh'].min():.2f} mm"
    )

    print(
        f"Maximum rainfall: "
        f"{df['rfh'].max():.2f} mm"
    )

    print("\nBaseline analysis completed successfully.")


if __name__ == "__main__":
    main()