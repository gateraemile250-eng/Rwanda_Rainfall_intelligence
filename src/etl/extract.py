"""
Extract Rwanda rainfall data from the project's raw CSV source.

This module provides reusable extraction functions for reading the
raw rainfall dataset and writing an intermediate copy to the staging
area for downstream ETL processing.
"""

import logging
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------

logger = logging.getLogger(__name__)


def extract_data(file_path):
    """
    Read the raw rainfall dataset from a CSV file.

    Parameters:
        file_path (str | Path): Path to the raw rainfall CSV file.

    Returns:
        pandas.DataFrame: Extracted raw rainfall data.
    """

    file_path = Path(file_path)

    logger.info("Starting rainfall data extraction.")
    logger.info("Source file: %s", file_path)

    if not file_path.exists():
        logger.error(
            "Rainfall source file not found: %s",
            file_path,
        )
        raise FileNotFoundError(
            f"Rainfall source file not found: {file_path}"
        )

    df = pd.read_csv(file_path)

    logger.info(
        "Rainfall data extracted successfully: %s rows, %s columns.",
        f"{len(df):,}",
        len(df.columns),
    )

    if "date" in df.columns:
        dates = pd.to_datetime(df["date"], errors="coerce")

        valid_dates = dates.dropna()

        if not valid_dates.empty:
            logger.info(
                "Source date range: %s to %s.",
                valid_dates.min().date(),
                valid_dates.max().date(),
            )

    return df


def extract_to_staging(source_path, staging_path):
    """
    Extract raw rainfall data and save it to the staging area.

    This function is designed for orchestrated ETL workflows such as
    Apache Airflow. The staged file provides durable intermediate
    storage between pipeline tasks.

    Parameters:
        source_path (str | Path): Path to the raw rainfall CSV file.
        staging_path (str | Path): Destination path for the staged CSV.

    Returns:
        str: Path to the staged rainfall file.
    """

    staging_path = Path(staging_path)

    logger.info("Starting extraction to staging.")

    # Ensure the staging directory exists.
    staging_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df = extract_data(source_path)

    df.to_csv(
        staging_path,
        index=False,
    )

    logger.info(
        "Staging file created successfully: %s (%s rows).",
        staging_path,
        f"{len(df):,}",
    )

    return str(staging_path)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
    )

    source_file = Path(
        "data/raw/rwa-rainfall-subnat-full.csv"
    )

    staging_file = Path(
        "data/staging/rainfall_extracted.csv"
    )

    extracted_path = extract_to_staging(
        source_file,
        staging_file,
    )

    logger.info(
        "Extraction completed: %s",
        extracted_path,
    )