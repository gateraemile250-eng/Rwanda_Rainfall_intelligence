"""
Create and refresh analytical PostgreSQL views.

This module executes the analytical SQL layer used by the
Rwanda Rainfall Intelligence dashboard and downstream analytics.
"""

import logging
from pathlib import Path

from sqlalchemy import text

from load import create_database_engine


# ---------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------
# Analytical SQL configuration
# ---------------------------------------------------------------------

DEFAULT_SQL_PATH = Path(
    "/opt/airflow/project/sql/03_create_dashboard_views.sql"
)


def create_analytical_views(sql_path=DEFAULT_SQL_PATH):
    """
    Create or replace the PostgreSQL analytical views.

    The SQL script is executed only after upstream ETL and database
    validation stages have completed successfully.

    Parameters:
        sql_path (str | Path):
            Path to the analytical views SQL script.

    Returns:
        dict: Analytical-view execution summary.

    Raises:
        FileNotFoundError:
            If the SQL script cannot be found.
        ValueError:
            If the SQL script is empty.
    """

    logger.info("Starting analytical view creation.")

    sql_path = Path(sql_path)

    logger.info(
        "Analytical SQL file: %s",
        sql_path,
    )

    if not sql_path.exists():
        logger.error(
            "Analytical SQL file not found: %s",
            sql_path,
        )
        raise FileNotFoundError(
            f"Analytical SQL file not found: {sql_path}"
        )

    sql_script = sql_path.read_text(
        encoding="utf-8"
    ).strip()

    if not sql_script:
        logger.error(
            "Analytical SQL script is empty: %s",
            sql_path,
        )
        raise ValueError(
            "Analytical view creation failed: "
            "SQL script is empty."
        )

    logger.info(
        "Analytical SQL script loaded successfully."
    )

    engine = create_database_engine()

    try:
        with engine.begin() as connection:
            connection.execute(
                text(sql_script)
            )

        logger.info(
            "Analytical views created successfully."
        )

        return {
            "status": "success",
            "sql_file": str(sql_path),
        }

    except Exception:
        logger.exception(
            "Analytical view creation failed."
        )
        raise

    finally:
        engine.dispose()
        logger.info(
            "PostgreSQL analytical-view database engine disposed."
        )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
    )

    result = create_analytical_views()

    logger.info(
        "Analytical view summary: %s",
        result,
    )