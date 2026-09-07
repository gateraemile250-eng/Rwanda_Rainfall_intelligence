# Rwanda Rainfall Intelligence

## Project Overview

Rwanda Rainfall Intelligence is a data engineering and analytics project focused on collecting, processing, storing, analyzing, and visualizing rainfall data across Rwanda.

The project transforms historical and current rainfall observations into reliable datasets and useful insights for understanding rainfall patterns, variability, trends, and extreme rainfall events.

The project combines **Data Engineering, Water Resources Engineering, and geospatial analysis** to build a foundation for rainfall intelligence and water-related decision support.

## Current Status

The project has progressed through **data preparation, database validation, and ETL pipeline development**.

### Completed

* Data ingestion and exploratory analysis
* Data quality assessment
* Missing-value investigation
* Administrative identifier validation
* Time-series consistency validation
* Rainfall value validation
* Data cleaning and transformation
* Processed dataset generation
* PostgreSQL database design
* PostgreSQL table creation
* Cleaned dataset loading into PostgreSQL
* Database data-quality validation
* ETL extraction module
* ETL transformation module
* ETL loading module
* Batch-based database loading
* Duplicate-protected database loading
* Idempotent ETL pipeline execution
* Full ETL pipeline validation
* Git version control and GitHub repository management

### Current Stage

**Phase 5 — ETL Pipeline**

The complete ETL pipeline has been successfully implemented and tested.

The pipeline extracts rainfall data from the raw CSV dataset, transforms and validates the records, and loads them into PostgreSQL using batch processing and duplicate protection.

### Next Stage

**Phase 6 — Rainfall Data Analysis**

The next stage will focus on analytical queries and rainfall intelligence, including:

* Rainfall trends
* Seasonal patterns
* Rainfall anomalies
* Extreme rainfall events
* Spatial rainfall patterns
* Historical rainfall comparisons

## Objectives

* Collect rainfall data for Rwanda
* Build a reliable data ingestion pipeline
* Clean and transform rainfall observations
* Store structured rainfall data in PostgreSQL
* Build reusable ETL processes
* Analyze rainfall patterns across locations and time
* Identify rainfall trends and extreme rainfall events
* Perform spatial rainfall analysis
* Create visualizations and dashboards
* Build a foundation for future rainfall forecasting
* Develop a data platform that can support water-resource decision making

## Technology Stack

* Python
* Pandas
* NumPy
* Matplotlib
* Seaborn
* PostgreSQL
* SQLAlchemy
* psycopg
* python-dotenv
* Requests
* Apache Airflow
* Apache Kafka
* Git
* GitHub

## Project Architecture

```text
Data Sources
     ↓
Data Ingestion
     ↓
Raw Data
     ↓
Data Exploration
     ↓
Data Cleaning & Validation
     ↓
Processed Data
     ↓
ETL Pipeline
     ↓
PostgreSQL
     ↓
Rainfall Analytics
     ↓
GIS / Spatial Analysis
     ↓
Dashboards & Decision Support
```

## Data Processing

### Data Ingestion and Exploration

The raw Rwanda rainfall dataset is loaded using Python and Pandas.

Initial exploration was performed to understand:

* Dataset structure
* Variables and data types
* Date coverage
* Administrative locations
* Missing values
* Duplicate records
* Rainfall distributions
* Data versions

### Data Cleaning and Validation

The cleaning stage included:

* Date conversion and validation
* Administrative identifier validation
* PCODE-to-location consistency checks
* Time-series consistency checks across locations
* Rainfall value validation
* Pixel-count validation
* Data version inspection
* Structured missing-value investigation
* Data type optimization
* Duplicate detection

Structured missing values in selected rainfall variables were retained because they occur systematically at the beginning of accumulation windows and there was insufficient evidence to justify imputation.

The cleaned dataset is saved as:

`data/processed/rwanda_rainfall_cleaned.csv`

### Data Quality Validation Results

The rainfall dataset was subjected to multiple validation checks before and after being loaded into PostgreSQL.

| Validation                                       | Result |
| ------------------------------------------------ | -----: |
| Total records                                    | 58,680 |
| Unique dates                                     |  1,630 |
| Administrative locations                         |     36 |
| Administrative levels                            |      2 |
| Unique PCODEs                                    |     35 |
| Missing `rfh` values                             |      0 |
| Negative rainfall values                         |      0 |
| Invalid pixel counts                             |      0 |
| Duplicate `(date, adm_id, version)` combinations |      0 |
| Final records                                    | 58,536 |
| Preliminary records                              |    108 |
| Forecast records                                 |     36 |

### Validation Findings

* All 36 administrative locations contain the same 1,630 dekadal dates.
* The dataset covers the period from **1981-01-01 to 2026-04-01**.
* Rainfall values contain no negative observations.
* All observations have valid positive `n_pixels` values.
* No duplicate `(date, adm_id, version)` combinations were found.
* Rainfall accumulation fields are internally consistent: `rfh ≤ r1h ≤ r3h` where values are available.
* Average rainfall fields are internally consistent: `rfh_avg ≤ r1h_avg ≤ r3h_avg` where values are available.
* Missing values in accumulation fields occur systematically at the beginning of accumulation windows and were retained as `NULL` rather than replaced with zero.
* Extreme rainfall observations were retained because high values may represent genuine rainfall events rather than data errors.
* The dataset contains `final`, `prelim`, and `forecast` versions. These were retained so that future analysis can explicitly select the appropriate version.
* A PCODE consistency anomaly was identified for `RW36`, which is associated with two different administrative IDs. The records were retained because they represent distinct observations and are not duplicate primary-key combinations.

## PostgreSQL Database

The rainfall dataset has been loaded into PostgreSQL.

Database:

`rwanda_rainfall`

Table:

`rainfall_observations`

The table uses a composite primary key consisting of:

```text
(date, adm_id, version)
```

This combination uniquely identifies each rainfall observation in the dataset.

### PostgreSQL Loading Validation

The ETL pipeline was tested against the PostgreSQL database.

* Dataset records: **58,680**
* PostgreSQL records after ETL execution: **58,680**
* Difference: **0**
* Unique primary-key combinations: **58,680**
* Duplicate primary-key combinations: **0**

The database therefore maintains the expected number of records without duplicate observations.

## ETL Pipeline

The project now contains a reusable ETL pipeline consisting of three main stages:

```text
Extract
   ↓
Transform
   ↓
Load
```

### Extract

The extraction module reads the raw rainfall CSV dataset using Pandas without modifying the source data.

File:

`src/etl/extract.py`

The extraction stage successfully processes:

**58,680 rows and 15 columns.**

### Transform

The transformation module standardizes column names and data types and performs rainfall-specific quality checks.

File:

`src/etl/transform.py`

Transformation checks include:

* Date validity
* Numeric data types
* Negative rainfall detection
* Invalid pixel-count detection
* Rainfall accumulation consistency
* Duplicate detection

The transformation stage successfully processes:

**58,680 rows and 15 columns.**

### Load

The loading module transfers transformed data into PostgreSQL.

File:

`src/etl/load.py`

The loader uses:

* PostgreSQL
* SQLAlchemy
* psycopg
* Batch loading
* Temporary staging tables
* Primary-key conflict handling

Records that already exist in PostgreSQL are skipped using:

```text
ON CONFLICT (date, adm_id, version) DO NOTHING
```

This prevents duplicate observations from being inserted.

### Idempotent Pipeline

The ETL pipeline is designed to be **idempotent**.

This means the pipeline can be executed repeatedly without creating duplicate records.

A controlled test demonstrated:

```text
First test run:
3 new rows inserted
0 duplicates skipped

Second test run:
0 new rows inserted
3 duplicates skipped
```

The full dataset was subsequently processed successfully:

```text
58,680 rows processed
0 new rows inserted
58,680 duplicate rows skipped
```

The final PostgreSQL database remained at:

```text
58,680 records
```

## ETL Pipeline Execution

The complete pipeline can be executed from the project root using:

```bash
python src/etl/pipeline.py
```

The pipeline performs:

```text
[1/3] EXTRACT
       ↓
[2/3] TRANSFORM
       ↓
[3/3] LOAD
```

## SQL Validation

Database validation queries are stored in:

```text
sql/
├── 01_create_rainfall_table.sql
└── 02_validate_rainfall_data.sql
```

These scripts support:

* Database table creation
* Row-count validation
* Date coverage validation
* Location validation
* Duplicate detection
* Missing-value checks
* Negative rainfall checks
* Pixel-count validation
* Rainfall accumulation consistency
* Data-version validation

## Project Structure

```text
Rwanda_Rainfall_intelligence/
│
├── data/
│   ├── raw/
│   │   └── rwa-rainfall-subnat-full.csv
│   │
│   └── processed/
│       └── rwanda_rainfall_cleaned.csv
│
├── Notebooks/
│   ├── 01 data explaration.py
│   └── 02_data_cleaning.py
│
├── src/
│   └── etl/
│       ├── extract.py
│       ├── transform.py
│       ├── load.py
│       └── pipeline.py
│
├── sql/
│   ├── 01_create_rainfall_table.sql
│   └── 02_validate_rainfall_data.sql
│
├── .gitignore
├── .env
└── README.md
```

> Note: Raw datasets and environment variables are excluded from version control through `.gitignore`.

## Project Roadmap

```text
Phase 1 — Project Setup
        ↓
Phase 2 — Data Exploration & Understanding
        ↓
Phase 3 — Data Cleaning & Quality Validation
        ↓
Phase 4 — Database & Data Storage
        ↓
Phase 5 — ETL Pipeline                     ← COMPLETED
        ↓
Phase 6 — Rainfall Data Analysis           ← NEXT
        ↓
Phase 7 — GIS & Spatial Intelligence
        ↓
Phase 8 — Dashboard & Decision Support
        ↓
Phase 9 — Productionization & Portfolio
```

## Future Development

The project will progressively incorporate:

* Advanced rainfall trend analysis
* Seasonal rainfall analysis
* Rainfall anomaly detection
* Extreme rainfall event detection
* Spatial rainfall analysis
* PostGIS spatial database integration
* GeoPandas-based geospatial processing
* Rainfall risk mapping
* Apache Airflow orchestration
* Apache Kafka streaming
* Analytical data modeling
* Interactive dashboards
* Rainfall forecasting
* Automated data quality monitoring
* Containerization with Docker
* Production-ready data pipelines

## Project Vision

Rwanda Rainfall Intelligence is intended to evolve from a rainfall analysis project into a broader **water and environmental data intelligence platform**.

The long-term goal is to combine rainfall data, geospatial information, hydrological analysis, and modern data engineering technologies to support better understanding of Rwanda's water and climate patterns.

## Author

**GATERA Emile**

**Civil & Data Water Engineer**

