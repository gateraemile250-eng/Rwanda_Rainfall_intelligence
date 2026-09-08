# Rwanda Rainfall Intelligence

## Project Overview

Rwanda Rainfall Intelligence is a data engineering and water-resources analytics project focused on collecting, processing, storing, analyzing, and visualizing rainfall data across Rwanda.

The project combines **Data Engineering, Water Resources Engineering, and geospatial analysis** to transform rainfall observations into reliable datasets and useful insights for water-related decision support.

## Current Status

**Phase 1–6 completed.** The project has progressed from data preparation and database development to ETL and rainfall intelligence analysis.

### Completed

* Data ingestion and exploratory analysis
* Data cleaning and quality validation
* Missing-value investigation
* Administrative identifier and time-series validation
* Processed dataset generation
* PostgreSQL database design and validation
* Reusable ETL pipeline
* Batch and duplicate-protected database loading
* Idempotent ETL execution
* Rainfall baseline analysis
* Rainfall seasonality analysis
* Long-term rainfall analysis
* Rainfall anomaly analysis
* Extreme rainfall analysis
* Location-level spatial rainfall analysis
* Extreme rainfall event dataset generation
* Git version control and GitHub repository management

## Phase 6 — Rainfall Data Analysis

Phase 6 analyzed historical **final** rainfall observations to understand rainfall patterns, variability, anomalies, extremes, and spatial differences.

### Key Findings

* Dataset contains **58,536 final observations** across **36 administrative locations**.
* Historical analysis covers **1981–2025** using complete years.
* Average rainfall shows strong seasonality, with **April** having the highest average dekadal rainfall (**57.79 mm**) and **July** the lowest (**3.04 mm**).
* Historical Rwanda-wide annual rainfall baseline is approximately **1,154.11 mm/year**.
* **2000** was the strongest dry year in the anomaly analysis (**−20.13%**).
* **2018** was the strongest wet year (**+19.95%**) and had the highest frequency of 99th-percentile extreme observations.
* The global **99th-percentile extreme threshold is 102.70 mm per dekadal observation**.
* **586 observations** exceed this threshold.
* **RW23** has the highest frequency of 99th-percentile rainfall observations.
* **RW22** recorded the highest individual rainfall observation at **228.17 mm**.
* Extreme rainfall is concentrated mainly during **March–May**, particularly April, with a secondary concentration during **October–November**.

These findings provide a **screening-level basis** for further investigation of drainage, erosion, water-resource planning, agricultural water management, and rainfall-related risk.

The analysis does not treat dekadal rainfall as infrastructure design rainfall. Detailed flood design, IDF analysis, and return-period assessment require appropriate temporal rainfall data and additional hydrological information.

### Phase 6 Analytical Outputs

```text
data/processed/
├── rwanda_rainfall_cleaned.csv
├── rainfall_yearly_anomalies.csv
├── rainfall_extreme_events.csv
└── rainfall_spatial_summary.csv
```

## PostgreSQL Database

Database:

```text
rwanda_rainfall
```

Table:

```text
rainfall_observations
```

Primary key:

```text
(date, adm_id, version)
```

The database contains **58,680 observations** across final, preliminary, and forecast versions.

## ETL Pipeline

The reusable ETL pipeline follows:

```text
Raw CSV
   ↓
Extract
   ↓
Transform & Validate
   ↓
Load
   ↓
PostgreSQL
```

Files:

```text
src/etl/
├── extract.py
├── transform.py
├── load.py
└── pipeline.py
```

The pipeline processes **58,680 rows** and uses batch loading, staging tables, primary-key conflict protection, and idempotent execution.

Run with:

```bash
python src/etl/pipeline.py
```

## SQL Validation

```text
sql/
├── 01_create_rainfall_table.sql
└── 02_validate_rainfall_data.sql
```

The SQL scripts support table creation, row-count validation, location checks, duplicate detection, missing-value checks, rainfall validation, and data-version validation.

## Project Structure

```text
Rwanda_Rainfall_intelligence/
│
├── data/
│   ├── raw/
│   │   └── rwa-rainfall-subnat-full.csv
│   └── processed/
│       ├── rwanda_rainfall_cleaned.csv
│       ├── rainfall_yearly_anomalies.csv
│       ├── rainfall_extreme_events.csv
│       └── rainfall_spatial_summary.csv
│
├── Notebooks/
│   ├── 01 data explaration.py
│   └── 02_data_cleaning.py
│
├── src/
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── rainfall_baseline.py
│   │   ├── rainfall_seasonality.py
│   │   ├── rainfall_trends.py
│   │   ├── rainfall_anomalies.py
│   │   ├── rainfall_extremes.py
│   │   └── rainfall_spatial.py
│   │
│   └── etl/
│       ├── extract.py
│       ├── transform.py
│       ├── load.py
│       └── pipeline.py
│
├── sql/
├── .gitignore
├── .env
└── README.md
```

> Raw datasets and environment variables are excluded from version control through `.gitignore`.

## Project Roadmap

```text
Phase 1 — Project Setup                         ✅
Phase 2 — Data Exploration & Understanding      ✅
Phase 3 — Data Cleaning & Quality Validation     ✅
Phase 4 — Database & Data Storage               ✅
Phase 5 — ETL Pipeline                          ✅
Phase 6 — Rainfall Data Analysis                ✅
Phase 7 — GIS & PostGIS Spatial Intelligence    → NEXT
Phase 8 — Dashboard & Decision Support          → FUTURE
Phase 9 — Productionization & Portfolio         → FUTURE
```

## Future Development

* GIS and PostGIS spatial analysis
* GeoPandas geospatial processing
* Rainfall risk mapping
* Interactive dashboards
* Hydrological indicators
* Apache Airflow orchestration
* Apache Kafka streaming
* Automated data-quality monitoring
* Docker containerization
* Rainfall forecasting

## Project Vision

Rwanda Rainfall Intelligence will evolve into a **water and environmental data intelligence platform**, combining rainfall data, geospatial information, hydrological analysis, and modern data engineering to support better water-resource and environmental decision-making.

## Author

**GATERA Emile**

**Civil & Data Water Engineer**


