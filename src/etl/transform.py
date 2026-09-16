"""
Transform and validate extracted Rwanda rainfall data.

This module provides reusable transformation functions for standardizing,
validating, and preparing Rwanda rainfall observations for loading into
PostgreSQL or downstream pipeline stages.
"""

import logging
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------
# Transformation configuration
# ---------------------------------------------------------------------

NUMERIC_COLUMNS = [
    "adm_level",
    "adm_id",
    "n_pixels",
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

REQUIRED_COLUMNS = {
    "date",
    "adm_level",
    "adm_id",
    "pcode",
    "n_pixels",
    "rfh",
    "rfh_avg",
    "r1h",
    "r1h_avg",
    "r3h",
    "r3h_avg",
    "rfq",
    "r1q",
    "r3q",
    "version",
}


def transform_data(df):
    """
    Transform and validate the extracted rainfall dataset.

    Parameters:
        df (pandas.DataFrame): Raw rainfall data.

    Returns:
        pandas.DataFrame: Transformed and validated rainfall data.

    Raises:
        ValueError: If critical data-quality rules are violated.
    """

    logger.info("Starting rainfall data transformation and validation.")
    logger.info(
        "Input dataset: %s rows, %s columns.",
        f"{len(df):,}",
        len(df.columns),
    )

    # Work on a copy to preserve the original DataFrame.
    df = df.copy()

    # Standardize column names.
    df.columns = df.columns.str.strip().str.lower()

    # Validate required columns before processing.
    missing_columns = REQUIRED_COLUMNS.difference(df.columns)

    if missing_columns:
        logger.error(
            "Required columns are missing: %s",
            sorted(missing_columns),
        )
        raise ValueError(
            "Transformation failed: required columns are missing: "
            f"{sorted(missing_columns)}"
        )

    logger.info("Required-column validation passed.")

    # Convert date values to datetime.
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
    )

    # Convert expected numeric fields.
    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    # Remove exact duplicate rows.
    duplicate_count = int(df.duplicated().sum())

    if duplicate_count > 0:
        logger.warning(
            "Removing %s exact duplicate rows.",
            f"{duplicate_count:,}",
        )
        df = df.drop_duplicates().reset_index(drop=True)
    else:
        logger.info("Duplicate-row validation passed: 0 duplicates.")

    # Validate date conversion.
    invalid_dates = int(df["date"].isna().sum())

    if invalid_dates > 0:
        logger.error(
            "Invalid date values found: %s",
            f"{invalid_dates:,}",
        )
        raise ValueError(
            "Transformation failed: "
            f"{invalid_dates:,} invalid date values found."
        )

    logger.info("Date validation passed: 0 invalid dates.")

    # Validate rainfall values.
    negative_rfh = int((df["rfh"] < 0).sum())

    if negative_rfh > 0:
        logger.error(
            "Negative rainfall values found: %s",
            f"{negative_rfh:,}",
        )
        raise ValueError(
            "Transformation failed: "
            f"{negative_rfh:,} negative rainfall values found."
        )

    logger.info("Rainfall validation passed: 0 negative rfh values.")

    # Validate pixel counts.
    invalid_pixels = int((df["n_pixels"] <= 0).sum())

    if invalid_pixels > 0:
        logger.error(
            "Invalid pixel counts found: %s",
            f"{invalid_pixels:,}",
        )
        raise ValueError(
            "Transformation failed: "
            f"{invalid_pixels:,} invalid pixel counts found."
        )

    logger.info("Pixel-count validation passed.")

    # Validate 1-month rainfall accumulation where values are available.
    invalid_r1h = int(
        (
            df["r1h"].notna()
            & df["rfh"].notna()
            & (df["r1h"] < df["rfh"])
        ).sum()
    )

    if invalid_r1h > 0:
        logger.error(
            "Records violating rfh <= r1h: %s",
            f"{invalid_r1h:,}",
        )
        raise ValueError(
            "Transformation failed: "
            f"{invalid_r1h:,} records violate rfh <= r1h."
        )

    logger.info("One-month accumulation validation passed.")

    # Validate 3-month rainfall accumulation where values are available.
    invalid_r3h = int(
        (
            df["r3h"].notna()
            & df["r1h"].notna()
            & (df["r3h"] < df["r1h"])
        ).sum()
    )

    if invalid_r3h > 0:
        logger.error(
            "Records violating r1h <= r3h: %s",
            f"{invalid_r3h:,}",
        )
        raise ValueError(
            "Transformation failed: "
            f"{invalid_r3h:,} records violate r1h <= r3h."
        )

    logger.info("Three-month accumulation validation passed.")

    logger.info(
        "Rainfall transformation and validation completed successfully: "
        "%s rows, %s columns.",
        f"{len(df):,}",
        len(df.columns),
    )

    return df


def transform_staged_data(staging_path, output_path):
    """
    Transform a staged rainfall CSV and save the validated result.

    This function is designed for orchestrated ETL workflows such as
    Apache Airflow. It reads the output of the extraction task, applies
    the project's transformation and validation rules, and writes a
    durable intermediate file for the loading task.

    Parameters:
        staging_path (str | Path): Path to the extracted staging CSV.
        output_path (str | Path): Destination for transformed data.

    Returns:
        str: Path to the transformed and validated CSV file.
    """

    staging_path = Path(staging_path)
    output_path = Path(output_path)

    logger.info(
        "Reading staged rainfall data: %s",
        staging_path,
    )

    if not staging_path.exists():
        logger.error(
            "Staged rainfall file not found: %s",
            staging_path,
        )
        raise FileNotFoundError(
            f"Staged rainfall file not found: {staging_path}"
        )

    df = pd.read_csv(staging_path)

    transformed_df = transform_data(df)

    # Ensure the destination directory exists.
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    transformed_df.to_csv(
        output_path,
        index=False,
    )

    logger.info(
        "Transformed staging file created successfully: "
        "%s (%s rows).",
        output_path,
        f"{len(transformed_df):,}",
    )

    return str(output_path)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
    )

    input_file = Path(
        "data/staging/rainfall_extracted.csv"
    )

    output_file = Path(
        "data/staging/rainfall_transformed.csv"
    )

    transformed_path = transform_staged_data(
        input_file,
        output_file,
    )

    logger.info(
        "Transformation completed: %s",
        transformed_path,
    )