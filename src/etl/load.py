"""
Load transformed Rwanda rainfall data into PostgreSQL.

This module provides reusable loading functions for inserting validated
Rwanda rainfall observations into PostgreSQL while preserving pipeline
idempotency and preventing duplicate primary-key records.
"""

import logging
import os
import re
import uuid
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.types import Date, Float, Integer, String


# ---------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------
# Database loading configuration
# ---------------------------------------------------------------------

DEFAULT_TABLE_NAME = "rainfall_observations"

REQUIRED_COLUMNS = [
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

COLUMN_TYPES = {
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


def validate_table_name(table_name):
    """
    Validate a PostgreSQL table name.

    Parameters:
        table_name (str): PostgreSQL table name.

    Raises:
        ValueError: If the table name contains unsafe characters.
    """

    if not re.fullmatch(
        r"[A-Za-z_][A-Za-z0-9_]*",
        table_name,
    ):
        logger.error(
            "Invalid PostgreSQL table name: %s",
            table_name,
        )
        raise ValueError(
            f"Invalid PostgreSQL table name: {table_name}"
        )


def create_database_engine():
    """
    Create a SQLAlchemy engine from environment variables.

    Required environment variables:
        DB_HOST
        DB_PORT
        DB_NAME
        DB_USER
        DB_PASSWORD

    Returns:
        sqlalchemy.engine.Engine: PostgreSQL database engine.

    Raises:
        ValueError: If required database configuration is missing.
    """

    load_dotenv()

    database_config = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }

    missing_variables = [
        variable
        for variable, value in {
            "DB_HOST": database_config["host"],
            "DB_PORT": database_config["port"],
            "DB_NAME": database_config["dbname"],
            "DB_USER": database_config["user"],
            "DB_PASSWORD": database_config["password"],
        }.items()
        if not value
    ]

    if missing_variables:
        logger.error(
            "Database configuration is incomplete. "
            "Missing variables: %s",
            ", ".join(missing_variables),
        )
        raise ValueError(
            "Database configuration is incomplete. "
            "Missing environment variables: "
            f"{', '.join(missing_variables)}"
        )

    logger.info(
        "Creating PostgreSQL connection for database '%s' "
        "on host '%s:%s'.",
        database_config["dbname"],
        database_config["host"],
        database_config["port"],
    )

    return create_engine(
        "postgresql+psycopg://",
        connect_args=database_config,
        pool_pre_ping=True,
    )


def validate_dataframe(df):
    """
    Validate that the DataFrame is ready for database loading.

    Parameters:
        df (pandas.DataFrame): Transformed rainfall data.

    Raises:
        ValueError: If required columns are missing or the dataset is empty.
    """

    if df.empty:
        logger.error("Transformed rainfall dataset is empty.")
        raise ValueError(
            "Database loading failed: transformed dataset is empty."
        )

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        logger.error(
            "Required loading columns are missing: %s",
            missing_columns,
        )
        raise ValueError(
            "Database loading failed: required columns are missing: "
            f"{missing_columns}"
        )

    logger.info(
        "Database-loading validation passed: %s rows ready.",
        f"{len(df):,}",
    )


def load_data(
    df,
    table_name=DEFAULT_TABLE_NAME,
    engine=None,
):
    """
    Load transformed rainfall data into PostgreSQL.

    Data is first written to a temporary staging table. Records are then
    inserted into the target table. Existing records with the same
    (date, adm_id, version) primary key are skipped.

    Parameters:
        df (pandas.DataFrame): Transformed rainfall data.
        table_name (str): Target PostgreSQL table name.
        engine (sqlalchemy.engine.Engine | None):
            Optional existing database engine.

    Returns:
        dict: Loading statistics containing input, inserted, and skipped rows.
    """

    logger.info("Starting PostgreSQL rainfall data loading.")

    validate_table_name(table_name)
    validate_dataframe(df)

    database_engine = engine or create_database_engine()

    staging_table = (
        f"{table_name}_staging_{uuid.uuid4().hex[:8]}"
    )

    column_list = ", ".join(REQUIRED_COLUMNS)

    inserted_rows = 0

    try:
        logger.info(
            "Writing %s rows to temporary PostgreSQL staging table.",
            f"{len(df):,}",
        )

        df[REQUIRED_COLUMNS].to_sql(
            staging_table,
            database_engine,
            if_exists="fail",
            index=False,
            dtype=COLUMN_TYPES,
            method="multi",
            chunksize=2000,
        )

        logger.info(
            "Temporary staging table created successfully: %s",
            staging_table,
        )

        with database_engine.begin() as connection:
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

            inserted_rows = max(
                result.rowcount or 0,
                0,
            )

            connection.execute(
                text(
                    f'DROP TABLE IF EXISTS "{staging_table}"'
                )
            )

        skipped_rows = len(df) - inserted_rows

        logger.info(
            "PostgreSQL loading completed successfully."
        )
        logger.info(
            "Load summary | input=%s | inserted=%s | skipped=%s",
            f"{len(df):,}",
            f"{inserted_rows:,}",
            f"{skipped_rows:,}",
        )

        return {
            "input_rows": len(df),
            "inserted_rows": inserted_rows,
            "skipped_rows": skipped_rows,
        }

    except Exception:
        logger.exception(
            "PostgreSQL rainfall data loading failed."
        )

        # Clean up the staging table if loading fails.
        try:
            with database_engine.begin() as connection:
                connection.execute(
                    text(
                        f'DROP TABLE IF EXISTS "{staging_table}"'
                    )
                )

            logger.info(
                "Temporary staging table cleaned up after failure."
            )

        except Exception:
            logger.exception(
                "Staging-table cleanup failed."
            )

        raise

    finally:
        if engine is None:
            database_engine.dispose()
            logger.info("PostgreSQL database engine disposed.")


def load_transformed_file(
    file_path,
    table_name=DEFAULT_TABLE_NAME,
):
    """
    Load a transformed rainfall CSV file into PostgreSQL.

    This wrapper is designed for orchestrated workflows such as
    Apache Airflow. Airflow can pass the transformed file path between
    tasks instead of transferring the full DataFrame through XCom.

    Parameters:
        file_path (str | Path): Path to the transformed rainfall CSV.
        table_name (str): Target PostgreSQL table name.

    Returns:
        dict: Database loading statistics.
    """

    file_path = Path(file_path)

    logger.info(
        "Reading transformed rainfall data: %s",
        file_path,
    )

    if not file_path.exists():
        logger.error(
            "Transformed rainfall file not found: %s",
            file_path,
        )
        raise FileNotFoundError(
            f"Transformed rainfall file not found: {file_path}"
        )

    df = pd.read_csv(
        file_path,
        parse_dates=["date"],
    )

    logger.info(
        "Transformed rainfall file loaded: %s rows.",
        f"{len(df):,}",
    )

    return load_data(
        df=df,
        table_name=table_name,
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
    )

    transformed_file = Path(
        "data/staging/rainfall_transformed.csv"
    )

    load_statistics = load_transformed_file(
        transformed_file
    )

    logger.info(
        "Loading summary: %s",
        load_statistics,
    )