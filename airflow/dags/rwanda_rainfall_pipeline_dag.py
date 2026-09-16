"""
Apache Airflow DAG for the Rwanda Rainfall Intelligence pipeline.

This DAG orchestrates extraction, transformation and validation,
PostgreSQL loading, database quality validation, and analytical
view preparation for downstream rainfall intelligence products.
"""

import sys
from datetime import timedelta

import pendulum
from airflow.sdk import DAG, task


# ---------------------------------------------------------------------
# Project module configuration
# ---------------------------------------------------------------------

ETL_PATH = "/opt/airflow/project/src/etl"

if ETL_PATH not in sys.path:
    sys.path.insert(0, ETL_PATH)

from extract import extract_to_staging
from load import load_transformed_file
from transform import transform_staged_data
from validate import validate_database
from views import create_analytical_views


# ---------------------------------------------------------------------
# Pipeline paths
# ---------------------------------------------------------------------

RAW_DATA_PATH = (
    "/opt/airflow/project/data/raw/"
    "rwa-rainfall-subnat-full.csv"
)

EXTRACTED_DATA_PATH = (
    "/opt/airflow/project/data/staging/"
    "rainfall_extracted.csv"
)

TRANSFORMED_DATA_PATH = (
    "/opt/airflow/project/data/staging/"
    "rainfall_transformed.csv"
)


# ---------------------------------------------------------------------
# Scheduling and default task configuration
# ---------------------------------------------------------------------

RWANDA_TIMEZONE = pendulum.timezone("Africa/Kigali")

default_args = {
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


# ---------------------------------------------------------------------
# DAG definition
# ---------------------------------------------------------------------

with DAG(
    dag_id="rwanda_rainfall_pipeline",
    description=(
        "Orchestrate the Rwanda Rainfall Intelligence ETL pipeline"
    ),
    start_date=pendulum.datetime(
        2026,
        9,
        1,
        tz=RWANDA_TIMEZONE,
    ),
    schedule="0 6 1,11,21 * *",
    catchup=False,
    default_args=default_args,
    tags=["rwanda", "rainfall", "etl"],
) as dag:

    @task(task_id="extract_rainfall")
    def extract_rainfall():
        """
        Extract the raw rainfall dataset into the staging area.

        Returns:
            str: Path to the extracted staging CSV file.
        """

        return extract_to_staging(
            source_path=RAW_DATA_PATH,
            staging_path=EXTRACTED_DATA_PATH,
        )

    @task(task_id="transform_validate")
    def transform_validate(extracted_file):
        """
        Transform and validate the extracted rainfall dataset.

        Parameters:
            extracted_file (str):
                Path returned by the extraction task.

        Returns:
            str: Path to the transformed and validated CSV file.
        """

        return transform_staged_data(
            staging_path=extracted_file,
            output_path=TRANSFORMED_DATA_PATH,
        )

    @task(task_id="load_postgresql")
    def load_postgresql(transformed_file):
        """
        Load transformed rainfall observations into PostgreSQL.

        Existing records with the same primary key are skipped,
        preserving pipeline idempotency.

        Parameters:
            transformed_file (str):
                Path returned by the transformation task.

        Returns:
            dict: PostgreSQL loading statistics.
        """

        return load_transformed_file(
            file_path=transformed_file,
        )

    @task(task_id="database_validation")
    def database_validation():
        """
        Validate critical data-quality conditions in PostgreSQL.

        The task fails if any critical quality gate is violated,
        preventing downstream analytical processing.

        Returns:
            dict: Database validation results.
        """

        return validate_database()

    @task(task_id="analytical_views")
    def analytical_views():
        """
        Create or replace PostgreSQL analytical views.

        This task prepares the validated rainfall data for downstream
        analytics, reporting, GIS, and dashboard consumption.

        Returns:
            dict: Analytical-view execution summary.
        """

        return create_analytical_views()

    # -----------------------------------------------------------------
    # Pipeline dependencies
    # -----------------------------------------------------------------

    extracted_file = extract_rainfall()

    transformed_file = transform_validate(
        extracted_file
    )

    load_result = load_postgresql(
        transformed_file
    )

    validation_result = database_validation()

    views_result = analytical_views()

    load_result >> validation_result >> views_result