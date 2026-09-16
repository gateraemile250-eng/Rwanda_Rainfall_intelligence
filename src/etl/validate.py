"""
Validate rainfall data stored in PostgreSQL.

This module provides automated database quality gates for the
Rwanda Rainfall Intelligence ETL pipeline. Critical validation
failures raise exceptions so orchestration systems such as Apache
Airflow can stop the pipeline before downstream processing.
"""

import logging

from sqlalchemy import text

from load import create_database_engine


# ---------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------
# Validation configuration
# ---------------------------------------------------------------------

DEFAULT_TABLE_NAME = "rainfall_observations"


def validate_database(table_name=DEFAULT_TABLE_NAME):
    """
    Run critical data-quality checks against PostgreSQL.

    Parameters:
        table_name (str): Rainfall observation table to validate.

    Returns:
        dict: Validation results for all quality gates.

    Raises:
        ValueError: If one or more critical quality checks fail.
    """

    logger.info(
        "Starting PostgreSQL rainfall data-quality validation."
    )

    engine = create_database_engine()

    validation_query = text(
        f"""
        SELECT
            COUNT(*) AS total_rows,

            COUNT(*) FILTER (
                WHERE rfh IS NULL
            ) AS missing_rfh,

            COUNT(*) FILTER (
                WHERE rfh < 0
                   OR rfh_avg < 0
                   OR r1h < 0
                   OR r1h_avg < 0
                   OR r3h < 0
                   OR r3h_avg < 0
            ) AS negative_rainfall,

            COUNT(*) FILTER (
                WHERE n_pixels IS NULL
                   OR n_pixels <= 0
            ) AS invalid_pixel_counts,

            COUNT(*) FILTER (
                WHERE r1h IS NOT NULL
                  AND rfh IS NOT NULL
                  AND r1h < rfh
            ) AS inconsistent_r1h,

            COUNT(*) FILTER (
                WHERE r3h IS NOT NULL
                  AND r1h IS NOT NULL
                  AND r3h < r1h
            ) AS inconsistent_r3h

        FROM {table_name}
        """
    )

    duplicate_query = text(
        f"""
        SELECT COUNT(*)
        FROM (
            SELECT
                date,
                adm_id,
                version
            FROM {table_name}
            GROUP BY
                date,
                adm_id,
                version
            HAVING COUNT(*) > 1
        ) AS duplicate_keys
        """
    )

    try:
        with engine.connect() as connection:
            row = connection.execute(
                validation_query
            ).mappings().one()

            duplicate_keys = connection.execute(
                duplicate_query
            ).scalar_one()

        results = {
            "total_rows": int(row["total_rows"]),
            "missing_rfh": int(row["missing_rfh"]),
            "duplicate_keys": int(duplicate_keys),
            "negative_rainfall": int(
                row["negative_rainfall"]
            ),
            "invalid_pixel_counts": int(
                row["invalid_pixel_counts"]
            ),
            "inconsistent_r1h": int(
                row["inconsistent_r1h"]
            ),
            "inconsistent_r3h": int(
                row["inconsistent_r3h"]
            ),
        }

        logger.info(
            "Database validation summary | "
            "total_rows=%s | missing_rfh=%s | "
            "duplicate_keys=%s | negative_rainfall=%s | "
            "invalid_pixel_counts=%s | inconsistent_r1h=%s | "
            "inconsistent_r3h=%s",
            f"{results['total_rows']:,}",
            results["missing_rfh"],
            results["duplicate_keys"],
            results["negative_rainfall"],
            results["invalid_pixel_counts"],
            results["inconsistent_r1h"],
            results["inconsistent_r3h"],
        )

        failures = {
            key: value
            for key, value in results.items()
            if key != "total_rows" and value != 0
        }

        if results["total_rows"] == 0:
            failures["total_rows"] = 0

        if failures:
            failure_summary = ", ".join(
                f"{key}={value}"
                for key, value in failures.items()
            )

            logger.error(
                "PostgreSQL data-quality validation FAILED: %s",
                failure_summary,
            )

            raise ValueError(
                "PostgreSQL data-quality validation failed: "
                f"{failure_summary}"
            )

        logger.info(
            "PostgreSQL data-quality validation PASSED: "
            "%s rows validated with 0 critical quality issues.",
            f"{results['total_rows']:,}",
        )

        return results

    except Exception:
        logger.exception(
            "PostgreSQL rainfall database validation failed."
        )
        raise

    finally:
        engine.dispose()
        logger.info(
            "PostgreSQL validation database engine disposed."
        )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
    )

    validation_results = validate_database()

    logger.info(
        "Validation summary: %s",
        validation_results,
    )