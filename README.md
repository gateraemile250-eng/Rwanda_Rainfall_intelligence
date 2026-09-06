# Rwanda Rainfall Intelligence

## Project Overview

Rwanda Rainfall Intelligence is a data engineering and analytics project focused on collecting, processing, storing, analyzing, and visualizing rainfall data across Rwanda.

The project transforms historical rainfall observations into reliable datasets and useful insights for understanding rainfall patterns, variability, trends, and extreme rainfall events.

## Current Status

The project is currently in the **data preparation stage**.

### Completed

* Data ingestion and exploratory analysis
* Data quality assessment
* Missing-value investigation
* Administrative identifier validation
* Time-series consistency validation
* Rainfall value validation
* Data cleaning and transformation
* Processed dataset generation
* Git version control and GitHub repository management

### Next Stage

* PostgreSQL database design and data loading

## Objectives

* Collect rainfall data for Rwanda
* Build a reliable data ingestion pipeline
* Clean and transform rainfall observations
* Store structured rainfall data in PostgreSQL
* Analyze rainfall patterns across locations and time
* Identify rainfall trends and extreme rainfall events
* Create visualizations and dashboards
* Build a foundation for future rainfall forecasting

## Technology Stack

* Python
* Pandas
* NumPy
* Matplotlib
* Seaborn
* PostgreSQL
* SQLAlchemy
* Requests
* Apache Airflow
* Apache Kafka
* Git and GitHub

## Project Architecture

```text
Data Sources
     ↓
Data Ingestion
     ↓
Raw Data
     ↓
Data Cleaning & Transformation
     ↓
Processed Data
     ↓
PostgreSQL
     ↓
Analytics
     ↓
Dashboards & Insights
```

## Data Processing

### Data Ingestion and Exploration

The raw Rwanda rainfall dataset is loaded using Python and Pandas. Initial exploration was performed to understand the dataset structure, variables, data types, missing values, and duplicate records.

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

Structured missing values in selected rainfall variables were retained because they occur systematically at the beginning of the time series and there was insufficient evidence to justify imputation.

The cleaned dataset is saved as:

`data/processed/rwanda_rainfall_cleaned.csv`

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
│   ├── 01_data_exploration.py
│   └── 02_data_cleaning.py
│
└── README.md
```

## Future Development

The project will progressively incorporate:

* Automated data ingestion
* Apache Airflow orchestration
* Apache Kafka streaming
* PostgreSQL data warehousing
* Spatial rainfall analysis
* Extreme rainfall detection
* Rainfall forecasting
* Interactive dashboards

## Author

**GATERA Emile**

Civil & Data Water Engineer
