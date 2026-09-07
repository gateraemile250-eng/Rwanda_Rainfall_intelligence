"""
Run the complete Rwanda rainfall ETL pipeline.

This module orchestrates data extraction, transformation,
and loading into the PostgreSQL database.
"""

from extract import extract_data
from transform import transform_data
from load import load_data


def run_pipeline():
    """
    Execute the complete rainfall ETL pipeline.

    Returns:
        None
    """

    print("=" * 60)
    print("RWANDA RAINFALL ETL PIPELINE")
    print("=" * 60)

    file_path = "data/raw/rwa-rainfall-subnat-full.csv"

    print("\n[1/3] EXTRACT")
    raw_data = extract_data(file_path)

    print("\n[2/3] TRANSFORM")
    transformed_data = transform_data(raw_data)

    print("\n[3/3] LOAD")
    load_data(transformed_data)

    print("\n" + "=" * 60)
    print("ETL PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()