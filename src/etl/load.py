"""
Load transformed Rwanda rainfall data into PostgreSQL.

This module provides a reusable function for loading rainfall
observations into the project's PostgreSQL database while preventing
duplicate primary-key records.
"""

import os
import re
import uuid

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.types import Date, Integer, Float, String


def load_data(df, table_name="rainfall_observations"):
    """
    Load transformed rainfall data into PostgreSQL.

    Existing records with the same primary key are skipped.
    New records are inserted.

    Parameters:
        df (pandas.DataFrame): Transformed rainfall data.
        table_name (str): Target PostgreSQL table name.

    Returns:
        None
    """

    print("Starting data loading...")

    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", table_name):
        raise ValueError("Invalid PostgreSQL table name.")

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

    staging_table = f"{table_name}_staging_{uuid.uuid4().hex[:8]}"

    column_types = {
        "date": Date(),
        "adm_level": Integer(),
        "adm_id": Integer(),
        "pcode": String(10),
        "n_pixels": Integer(),
        "rfh": Float(),
        "rfh_avg": Float(),
        "r1h": Float(),
        "r1h_avg": Float(),
        "r3h": Float(),
        "r3h_avg": Float(),
        "rfq": Float(),
        "r1q": Float(),
        "r3q": Float(),
        "version": String(20),
    }

    columns = [
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
    ]

    column_list = ", ".join(columns)

    try:
        df.to_sql(
    staging_table,
    engine,
    if_exists="replace",
    index=False,
    dtype=column_types,
    method="multi",
    chunksize=2000,
)
        

        with engine.begin() as connection:
            result = connection.execute(
                text(
                    f"""
                    INSERT INTO {table_name} ({column_list})
                    SELECT {column_list}
                    FROM {staging_table}
                    ON CONFLICT (date, adm_id, version)
                    DO NOTHING
                    """
                )
            )

            inserted_rows = result.rowcount

            connection.execute(
                text(f'DROP TABLE IF EXISTS "{staging_table}"')
            )

        skipped_rows = len(df) - inserted_rows

        print(
            f"Data loading completed successfully: "
            f"{inserted_rows:,} new rows inserted."
        )

        print(
            f"Duplicate rows skipped: "
            f"{skipped_rows:,}"
        )

    except Exception:
        with engine.begin() as connection:
            connection.execute(
                text(f'DROP TABLE IF EXISTS "{staging_table}"')
            )

        raise