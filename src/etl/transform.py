"""
Transform and validate extracted Rwanda rainfall data.

This module applies standardized data types, column naming conventions,
duplicate handling, and rainfall-specific quality checks to the raw
rainfall dataset before it is loaded into PostgreSQL.
"""

import pandas as pd


def transform_data(df):
    """
    Transform and validate the extracted rainfall dataset.

    Parameters:
        df (pandas.DataFrame): Raw rainfall data extracted from the CSV source.

    Returns:
        pandas.DataFrame: Transformed and validated rainfall data.
    """

    print("Starting data transformation...")

    # Create a copy to avoid modifying the original extracted DataFrame.
    df = df.copy()

    # Standardize column names.
    df.columns = df.columns.str.lower()

    # Convert date to datetime.
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Define numeric columns.
    numeric_columns = [
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

    # Convert numeric columns to numeric data types.
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Remove exact duplicate rows.
    duplicate_count = df.duplicated().sum()

    if duplicate_count > 0:
        print(f"Removing {duplicate_count:,} exact duplicate rows...")
        df = df.drop_duplicates()

    # Validate date conversion.
    invalid_dates = df["date"].isna().sum()

    if invalid_dates > 0:
        raise ValueError(
            f"Transformation failed: {invalid_dates:,} invalid date values found."
        )

    # Validate rainfall values.
    negative_rfh = (df["rfh"] < 0).sum()

    if negative_rfh > 0:
        raise ValueError(
            f"Transformation failed: {negative_rfh:,} negative rainfall values found."
        )

    # Validate pixel counts.
    invalid_pixels = (df["n_pixels"] <= 0).sum()

    if invalid_pixels > 0:
        raise ValueError(
            f"Transformation failed: {invalid_pixels:,} invalid pixel counts found."
        )

    # Validate rainfall accumulation relationships where values are available.
    invalid_r1h = (
        df["r1h"].notna()
        & df["rfh"].notna()
        & (df["r1h"] < df["rfh"])
    ).sum()

    if invalid_r1h > 0:
        raise ValueError(
            f"Transformation failed: {invalid_r1h:,} records violate rfh <= r1h."
        )

    invalid_r3h = (
        df["r3h"].notna()
        & df["r1h"].notna()
        & (df["r3h"] < df["r1h"])
    ).sum()

    if invalid_r3h > 0:
        raise ValueError(
            f"Transformation failed: {invalid_r3h:,} records violate r1h <= r3h."
        )

    print(
        f"Data transformation completed successfully: "
        f"{df.shape[0]:,} rows, {df.shape[1]} columns"
    )

    return df


if __name__ == "__main__":
    from extract import extract_data

    file_path = "data/raw/rwa-rainfall-subnat-full.csv"

    raw_df = extract_data(file_path)

    transformed_df = transform_data(raw_df)

    print("\nTransformed data preview:")
    print(transformed_df.head())

    print("\nData types:")
    print(transformed_df.dtypes)