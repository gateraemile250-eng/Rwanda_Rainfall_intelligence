"""
Extreme rainfall analysis for Rwanda.

Uses final observations to analyze rainfall extremes by:
- fixed thresholds
- percentiles
- location
- month
- year
- individual extreme observations
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
        SELECT date, adm_level, adm_id, pcode, rfh
        FROM rainfall_observations
        WHERE version = 'final'
        ORDER BY date, adm_id;
    """

    return pd.read_sql(query, engine)


def calculate_thresholds(df):
    """Calculate exploratory fixed rainfall thresholds."""

    thresholds = [50, 100, 150, 200]
    total = len(df)

    results = []

    for threshold in thresholds:
        count = (df["rfh"] >= threshold).sum()

        results.append({
            "threshold_mm": threshold,
            "extreme_observation_count": count,
            "percentage_of_observations": count / total * 100,
        })

    return pd.DataFrame(results)


def calculate_percentiles(df):
    """Calculate data-driven 95th and 99th percentile thresholds."""

    results = []

    for percentile in [0.95, 0.99]:
        threshold = df["rfh"].quantile(percentile)
        count = (df["rfh"] >= threshold).sum()

        results.append({
            "percentile": int(percentile * 100),
            "threshold_mm": threshold,
            "extreme_observation_count": count,
            "percentage_of_observations": count / len(df) * 100,
        })

    return pd.DataFrame(results)


def calculate_location_extremes(df):
    """Compare extreme rainfall frequency and magnitude by location."""

    p95 = df["rfh"].quantile(0.95)
    p99 = df["rfh"].quantile(0.99)

    result = (
        df.groupby(
            ["adm_level", "adm_id", "pcode"],
            as_index=False
        )
        .agg(
            total_observations=("rfh", "count"),
            extreme_95_count=("rfh", lambda x: (x >= p95).sum()),
            extreme_99_count=("rfh", lambda x: (x >= p99).sum()),
            above_100mm_count=("rfh", lambda x: (x >= 100).sum()),
            above_150mm_count=("rfh", lambda x: (x >= 150).sum()),
            maximum_rainfall_mm=("rfh", "max"),
        )
    )

    result["extreme_95_percent"] = (
        result["extreme_95_count"]
        / result["total_observations"]
        * 100
    )

    result["extreme_99_percent"] = (
        result["extreme_99_count"]
        / result["total_observations"]
        * 100
    )

    return result


def calculate_monthly_extremes(df):
    """Analyze extreme rainfall by month."""

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.month_name()

    p95 = df["rfh"].quantile(0.95)
    p99 = df["rfh"].quantile(0.99)

    result = (
        df.groupby(
            ["month", "month_name"],
            as_index=False
        )
        .agg(
            total_observations=("rfh", "count"),
            extreme_95_count=("rfh", lambda x: (x >= p95).sum()),
            extreme_99_count=("rfh", lambda x: (x >= p99).sum()),
            above_100mm_count=("rfh", lambda x: (x >= 100).sum()),
            above_150mm_count=("rfh", lambda x: (x >= 150).sum()),
            maximum_rainfall_mm=("rfh", "max"),
        )
    )

    result["extreme_95_percent"] = (
        result["extreme_95_count"]
        / result["total_observations"]
        * 100
    )

    result["extreme_99_percent"] = (
        result["extreme_99_count"]
        / result["total_observations"]
        * 100
    )

    return result


def calculate_yearly_extremes(df):
    """Analyze extreme rainfall by complete year."""

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year

    p95 = df["rfh"].quantile(0.95)
    p99 = df["rfh"].quantile(0.99)

    result = (
        df.groupby("year", as_index=False)
        .agg(
            total_observations=("rfh", "count"),
            location_count=("adm_id", "nunique"),
            extreme_95_count=("rfh", lambda x: (x >= p95).sum()),
            extreme_99_count=("rfh", lambda x: (x >= p99).sum()),
            above_100mm_count=("rfh", lambda x: (x >= 100).sum()),
            above_150mm_count=("rfh", lambda x: (x >= 150).sum()),
            above_200mm_count=("rfh", lambda x: (x >= 200).sum()),
            maximum_rainfall_mm=("rfh", "max"),
        )
    )

    # Keep complete years: 36 locations × 36 dekads = 1,296 observations
    result = result[
        (result["total_observations"] == 1296)
        & (result["location_count"] == 36)
    ].copy()

    result["extreme_95_percent"] = (
        result["extreme_95_count"]
        / result["total_observations"]
        * 100
    )

    result["extreme_99_percent"] = (
        result["extreme_99_count"]
        / result["total_observations"]
        * 100
    )

    return result


def create_extreme_event_dataset(df):
    """
    Create a reusable dataset of observations above
    the global 99th-percentile rainfall threshold.
    """

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.month_name()

    p95 = df["rfh"].quantile(0.95)
    p99 = df["rfh"].quantile(0.99)

    df["percentile_95_threshold_mm"] = p95
    df["percentile_99_threshold_mm"] = p99

    df["is_extreme_95"] = df["rfh"] >= p95
    df["is_extreme_99"] = df["rfh"] >= p99

    df["above_100mm"] = df["rfh"] >= 100
    df["above_150mm"] = df["rfh"] >= 150
    df["above_200mm"] = df["rfh"] >= 200

    events = df[df["is_extreme_99"]].copy()

    events["severity_class"] = pd.cut(
        events["rfh"],
        bins=[p99, 150, 200, float("inf")],
        labels=[
            "Extreme",
            "Very Extreme",
            "Exceptional",
        ],
        include_lowest=True,
    )

    columns = [
        "date",
        "year",
        "month",
        "month_name",
        "adm_level",
        "adm_id",
        "pcode",
        "rfh",
        "percentile_95_threshold_mm",
        "percentile_99_threshold_mm",
        "is_extreme_95",
        "is_extreme_99",
        "above_100mm",
        "above_150mm",
        "above_200mm",
        "severity_class",
    ]

    return (
        events[columns]
        .sort_values("rfh", ascending=False)
        .reset_index(drop=True)
    )


def save_extreme_event_dataset(events):
    """Save extreme rainfall observations as a processed dataset."""

    path = "data/processed/rainfall_extreme_events.csv"

    events.to_csv(path, index=False)

    print(f"\nExtreme event dataset saved to: {path}")


if __name__ == "__main__":

    print("=" * 60)
    print("RWANDA EXTREME RAINFALL ANALYSIS")
    print("=" * 60)

    # 1. Load data
    print("\n[1/6] Loading rainfall data...")
    df = load_rainfall_data()
    print(f"Loaded {len(df):,} final observations.")

    # 2. Fixed thresholds and percentiles
    print("\n[2/6] Calculating rainfall thresholds...")

    print("\nFixed thresholds:")
    print(
        calculate_thresholds(df)
        .to_string(index=False)
    )

    print("\nPercentile thresholds:")
    print(
        calculate_percentiles(df)
        .to_string(index=False)
    )

    # 3. Location extremes
    print("\n[3/6] Calculating extremes by location...")

    location_extremes = calculate_location_extremes(df)

    print("\nTop locations by 99th-percentile frequency:")
    print(
        location_extremes
        .sort_values("extreme_99_count", ascending=False)
        .head(10)
        .to_string(index=False)
    )

    # 4. Monthly extremes
    print("\n[4/6] Calculating extremes by month...")

    monthly_extremes = calculate_monthly_extremes(df)

    print(
        monthly_extremes.to_string(index=False)
    )

    # 5. Yearly extremes
    print("\n[5/6] Calculating extremes by year...")

    yearly_extremes = calculate_yearly_extremes(df)

    print("\nTop years by 99th-percentile frequency:")
    print(
        yearly_extremes
        .sort_values("extreme_99_count", ascending=False)
        .head(10)
        .to_string(index=False)
    )

    print("\nTop years by maximum rainfall:")
    print(
        yearly_extremes
        .sort_values("maximum_rainfall_mm", ascending=False)
        .head(10)
        .to_string(index=False)
    )

    # 6. Extreme observation dataset
    print("\n[6/6] Creating extreme rainfall dataset...")

    extreme_events = create_extreme_event_dataset(df)

    print(
        f"Extreme observations identified: "
        f"{len(extreme_events):,}"
    )

    print("\nTop extreme observations:")
    print(
        extreme_events
        .head(20)
        .to_string(index=False)
    )

    save_extreme_event_dataset(extreme_events)

    print("\n" + "=" * 60)
    print("EXTREME RAINFALL ANALYSIS COMPLETED SUCCESSFULLY")
    print("=" * 60)