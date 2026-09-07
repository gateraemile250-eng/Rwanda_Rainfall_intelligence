"""
Extract rainfall data from the project's raw CSV source.

This module provides a reusable extraction function that reads the
raw Rwanda rainfall dataset into a Pandas DataFrame without applying
any transformation or cleaning.
"""

import pandas as pd


def extract_data(file_path):
    """
    Read the raw rainfall dataset from a CSV file.

    Parameters:
        file_path (str): Path to the raw rainfall CSV file.

    Returns:
        pandas.DataFrame: Extracted raw rainfall data.
    """

    print("Starting data extraction...")

    df = pd.read_csv(file_path)

    print(
        f"Data extracted successfully: "
        f"{df.shape[0]:,} rows, {df.shape[1]} columns"
    )

    return df


if __name__ == "__main__":
    file_path = "data/raw/rwa-rainfall-subnat-full.csv"

    df = extract_data(file_path)

    print("\nFirst 5 rows:")
    print(df.head())