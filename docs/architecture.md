# Rwanda Rainfall Intelligence — System Architecture

## 1. Overview

**Rwanda Rainfall Intelligence** is an end-to-end data engineering and analytics project for processing, validating, storing, analyzing, and visualizing rainfall observations across Rwanda.

The system integrates:

- Python for ETL processing and data validation
- Apache Airflow for workflow orchestration and scheduling
- PostgreSQL for persistent data storage and analytical views
- Docker Compose for containerized infrastructure
- Power BI for interactive rainfall intelligence dashboards
- QGIS for spatial analysis and mapping

The architecture provides a reproducible workflow that transforms raw rainfall observations into validated, analysis-ready data and downstream decision-support products.

---

## 2. High-Level Architecture

```text
Raw Rainfall CSV
       |
       v
Apache Airflow
       |
       v
Python ETL Pipeline
       |
       +-- Extract
       |
       +-- Transform & Validate
       |
       +-- Load
       |
       v
PostgreSQL
       |
       +-- Database Quality Validation
       |
       v
Analytical SQL Views
       |
       +-------------------+
       |                   |
       v                   v
    Power BI              QGIS
    Dashboard        Spatial Analysis
```

At runtime, Apache Airflow orchestrates the Python ETL workflow. PostgreSQL provides persistent storage and the analytical SQL layer, while Power BI and QGIS consume prepared data for business intelligence and spatial analysis.

---

## 3. Data Source

The pipeline processes Rwanda subnational rainfall observations stored in CSV format.

The source dataset contains temporal and administrative identifiers together with rainfall measurements, historical averages, rainfall anomaly indicators, pixel counts, and dataset-version information.

The raw source data is stored under:

`data/raw/`

Raw data is kept separate from staging and processed outputs to preserve the original source and maintain a clear data-processing lifecycle.

---

## 4. ETL Pipeline

The ETL implementation is located under:

`src/etl/`

The pipeline is modular, with each component responsible for a specific stage of the data lifecycle.

### 4.1 Extract

**Module:** `extract.py`

The extraction stage:

- reads the raw rainfall CSV
- performs initial source checks
- records dataset dimensions and date coverage
- writes extracted data to the staging area

### 4.2 Transform and Validate

**Module:** `transform.py`

The transformation stage applies data-type conversions and performs quality checks covering:

- required columns
- date validity
- duplicate records
- rainfall values
- pixel counts
- rolling rainfall consistency

Expected historical missing values in rolling rainfall variables are retained rather than artificially imputed.

### 4.3 Load

**Module:** `load.py`

The loading stage writes transformed rainfall observations to PostgreSQL.

A temporary staging table and conflict-safe insertion strategy are used to protect the target table during loading.

The database primary key is:

`(date, adm_id, version)`

This design makes repeated pipeline execution **idempotent**. Records that already exist are skipped rather than duplicated, while new primary-key combinations can be inserted.

### 4.4 Database Validation

**Module:** `validate.py`

After loading, automated database quality gates verify the integrity of the stored rainfall data.

Validation checks include:

- total row count
- duplicate primary keys
- missing critical rainfall values
- negative rainfall values
- invalid pixel counts
- one-month rainfall consistency
- three-month rainfall consistency

A failed critical quality check causes the validation stage to fail rather than allowing the pipeline to silently continue.

### 4.5 Analytical Views

**Module:** `views.py`

The final ETL stage executes the analytical SQL layer used to prepare structured datasets for downstream analysis and visualization.

The analytical views support:

- annual rainfall analysis
- annual rainfall anomalies
- monthly rainfall seasonality
- district-level rainfall intelligence
- district reference information
- extreme-rainfall screening

---

## 5. Apache Airflow Orchestration

Apache Airflow orchestrates the production ETL workflow.

The production DAG is:

`rwanda_rainfall_pipeline`

The task dependency chain is:

```text
extract_rainfall
       |
       v
transform_validate
       |
       v
load_postgresql
       |
       v
database_validation
       |
       v
analytical_views
```

Each task represents a defined stage of the production pipeline, allowing execution status, failures, retries, duration, and logs to be monitored independently.

### Scheduling

The production schedule is:

```text
0 6 1,11,21 * *
```

The pipeline is scheduled for **06:00 Rwanda time on the 1st, 11th, and 21st of each month**.

This is the project's operational processing schedule. It does not imply that the upstream rainfall source publishes new data at exactly that time.

### Reliability and Monitoring

The Airflow workflow includes:

- automatic task retries
- retry delays
- structured application logging
- task-level execution monitoring
- DAG-run monitoring
- failure visibility through the Airflow web interface

Catch-up execution is disabled to prevent Airflow from automatically creating historical scheduled runs when the environment has been offline.

---

## 6. Docker Architecture

Docker Compose provides the containerized runtime environment for the production pipeline.

The environment contains the following services:

- Airflow API server
- Airflow scheduler
- Airflow worker
- Airflow DAG processor
- Airflow triggerer
- Redis
- PostgreSQL for Airflow metadata
- PostgreSQL for Rwanda rainfall data

### Separation of Databases

Two PostgreSQL services are used for different responsibilities.

**Airflow metadata PostgreSQL** stores Airflow's internal operational information, including DAG runs, task instances, scheduling metadata, and other Airflow state.

**Rainfall PostgreSQL** stores the actual Rwanda rainfall observations and analytical database objects.

Keeping these databases separate prevents Airflow's internal metadata from being mixed with the project's analytical data.

### Project Mounts

Project directories are mounted into the Airflow containers so that the orchestration environment can access:

- Airflow DAG definitions
- Python ETL modules
- rainfall source and staging data
- SQL scripts

### Persistence

A named Docker volume provides persistent storage for the rainfall PostgreSQL database.

This allows containers to be recreated without deleting the stored rainfall observations.

---

## 7. PostgreSQL Data Layer

The main rainfall database is:

`rwanda_rainfall`

The core table is:

`rainfall_observations`

The database schema is defined in:

`sql/01_create_rainfall_table.sql`

The primary key is:

`(date, adm_id, version)`

This key protects the database from duplicate observations during repeated ETL execution.

### Database Initialization

For a fresh Docker PostgreSQL volume, the schema initialization script is mounted into PostgreSQL's initialization directory:

`/docker-entrypoint-initdb.d/`

The schema uses:

```sql
CREATE TABLE IF NOT EXISTS rainfall_observations
```

This makes table creation safe to execute when the table already exists.

### Analytical SQL Layer

Analytical SQL views transform the stored observations into structures suitable for downstream analysis.

The analytical layer includes views for:

- district rainfall
- annual rainfall
- annual rainfall anomalies
- monthly seasonality
- district reference information
- extreme rainfall events

This separates raw database storage from analysis-ready representations.

---

## 8. Data Quality Strategy

Data quality is enforced at multiple stages rather than through a single final check.

```text
Source Data
    |
    v
Extraction Checks
    |
    v
Transformation Validation
    |
    v
PostgreSQL Constraints
    |
    v
Database Quality Gates
    |
    v
Analytical Views
```

This layered approach helps detect problems before invalid data reaches downstream analytical products.

The pipeline deliberately retains expected early-series missing values in rolling rainfall variables where insufficient historical observations exist to calculate those metrics.

Critical quality failures, such as duplicate database keys, missing critical rainfall values, negative rainfall, or invalid pixel counts, are treated as pipeline failures.

---

## 9. Environment and Secret Management

Runtime configuration is managed through environment variables.

Local configuration and credentials are stored in:

`.env`

The real `.env` file is excluded from Git and must not be committed to the repository.

A safe configuration template is provided through:

`.env.example`

The template documents the environment variables required to run the project while using placeholders for sensitive values such as database passwords and cryptographic keys.

Required configuration includes:

- Airflow user configuration
- Airflow Fernet key
- Airflow API authentication JWT secret
- rainfall PostgreSQL host
- rainfall PostgreSQL port
- database name
- database user
- database password

---

## 10. Analytics and Visualization

The engineering pipeline supports two primary downstream analytical environments.

### 10.1 Power BI

Power BI provides interactive rainfall intelligence dashboards covering:

- rainfall overview
- trends and seasonality
- district-level intelligence
- extreme rainfall and decision support

The dashboard uses prepared analytical data rather than performing the complete engineering workflow inside the visualization layer.

### 10.2 QGIS

QGIS provides geospatial analysis and mapping of rainfall indicators across Rwanda's administrative boundaries.

The GIS workflow supports district-level rainfall mapping and spatial interpretation of rainfall patterns.

District-level rainfall statistics use the project's documented aggregation methodology, including pixel-weighted aggregation where applicable.

---

## 11. Production Characteristics

The implemented architecture provides:

- modular Python ETL processing
- containerized infrastructure
- Apache Airflow orchestration
- scheduled pipeline execution
- retry and failure handling
- structured logging
- automated data-quality validation
- PostgreSQL persistence
- database constraints
- conflict-safe and idempotent loading
- reproducible database initialization
- analytical SQL views
- Airflow operational monitoring
- downstream BI and GIS integration

The result is a reproducible data-engineering workflow that moves rainfall observations from raw source data through validation and persistent storage to analysis-ready datasets and decision-support products.

---

## 12. End-to-End Data Flow

A complete production run follows this sequence:

1. Airflow starts the scheduled or manually triggered DAG.
2. `extract_rainfall` reads the raw rainfall CSV and writes the staging dataset.
3. `transform_validate` cleans, transforms, and validates the extracted observations.
4. `load_postgresql` loads valid observations into PostgreSQL using conflict-safe insertion.
5. `database_validation` runs quality gates against the stored data.
6. `analytical_views` prepares the analytical SQL layer.
7. Power BI and QGIS use prepared data for analytical and spatial products.

Repeated execution does not duplicate existing rainfall observations because the PostgreSQL primary key and conflict-handling strategy enforce idempotent loading.