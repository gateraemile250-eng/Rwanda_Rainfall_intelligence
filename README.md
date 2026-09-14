# Rwanda Rainfall Intelligence

## Project Overview

**Rwanda Rainfall Intelligence** is an end-to-end data engineering, geospatial analytics, and water-resources intelligence project developed to process, validate, store, analyze, map, and visualize historical rainfall data across Rwanda.

The project combines **Data Engineering, Water Resources Engineering, GIS, SQL, PostgreSQL, Python, QGIS, and Power BI** to transform raw subnational rainfall observations into structured datasets and decision-support information.

The complete workflow follows:

```text
Raw Rainfall Data
        ↓
Python Exploration & Validation
        ↓
Data Cleaning & Transformation
        ↓
PostgreSQL Database
        ↓
Reusable ETL Pipeline
        ↓
Rainfall Analysis
        ↓
GIS & Spatial Analysis
        ↓
SQL Analytical Views
        ↓
Power BI Dashboard
        ↓
Water-Resources Decision Support
```

---

## Project Status

**Phases 1–8 completed.**

The project has progressed from raw rainfall ingestion through database engineering, ETL development, historical rainfall analysis, GIS mapping, and an interactive Power BI decision-support dashboard.

### Completed

- Data ingestion and exploratory analysis
- Data cleaning and quality validation
- Missing-value and time-series investigation
- Administrative identifier validation
- PostgreSQL database design and validation
- Reusable and idempotent ETL pipeline
- Rainfall baseline and seasonality analysis
- Long-term trend and anomaly analysis
- Extreme rainfall analysis
- District-level rainfall aggregation
- Rwanda administrative boundary integration
- GIS spatial joins and choropleth mapping
- SQL analytical views for business intelligence
- Interactive Power BI dashboard
- Dashboard KPI validation against PostgreSQL
- Portfolio-ready GIS and dashboard exports
- Git version control and GitHub repository management

---

## Phase 8 — Rainfall Intelligence Dashboard

Phase 8 transformed the analytical outputs into an interactive **Power BI rainfall intelligence and decision-support dashboard**.

The dashboard is designed to answer four main questions:

1. What are Rwanda's major historical rainfall characteristics?
2. How has rainfall varied over time and through the annual seasonal cycle?
3. How does rainfall vary geographically between districts?
4. When and where have unusually high rainfall observations occurred?

### Dashboard Architecture

```text
PostgreSQL
    ↓
District-Level Analytical Views
    ↓
Annual / Monthly / Extreme Rainfall Views
    ↓
Power BI Data Model
    ↓
DAX Measures & KPIs
    ↓
Interactive Dashboard
```

The Power BI reporting layer uses **PostgreSQL analytical views** rather than directly analyzing the raw CSV.

This provides a clear separation between data storage, transformation, analytical modeling, and visualization.

---

## Dashboard Page 1 — Rainfall Overview

![Rainfall Overview](dashboard/exports/01_Rainfall_Overview.png)

The overview provides a high-level summary of Rwanda's historical rainfall conditions.

### Key Indicators

- **Historical annual rainfall baseline:** 1,130.36 mm/year
- **Wettest year:** 2018
- **Wettest annual rainfall:** 1,365.46 mm
- **Driest year:** 2000
- **Driest annual rainfall:** 909.01 mm
- **Extreme district-level rainfall observations:** 487
- **Extreme rainfall threshold:** 103.00 mm

The annual rainfall chart compares yearly rainfall totals against the long-term historical baseline for **1981–2025**.

---

## Dashboard Page 2 — Trends & Seasonality

![Rainfall Trends and Seasonality](dashboard/exports/02_Trends_Seasonality.png)

This page examines rainfall variability through time.

It includes:

- Annual rainfall compared with the historical baseline
- Historical monthly rainfall seasonality
- Annual rainfall anomalies

The monthly rainfall profile shows Rwanda's characteristic seasonal cycle, including a major rainfall peak around **April**, a pronounced dry period around **July**, and a secondary rainfall increase later in the year.

Annual anomalies highlight years that were substantially wetter or drier than the long-term baseline.

---

## Dashboard Page 3 — District Intelligence

![District Rainfall Intelligence](dashboard/exports/03_District_Intelligence.png)

The District Intelligence page connects rainfall observations with Rwanda's **30 administrative districts**.

It includes:

- Interactive district rainfall map
- Historical district rainfall profile
- Long-term average comparison
- District rainfall ranking
- District selection and filtering

The spatial analysis shows generally higher mean rainfall in **western and southwestern Rwanda**, while several eastern districts fall within lower historical mean-rainfall ranges.

### RW36 / Rusizi Aggregation

The source rainfall dataset contained two administrative identifiers associated with **PCODE RW36 (Rusizi)**.

Because the two records represented different rainfall aggregations with different pixel coverage, they were consolidated at **PCODE and date level using pixel-weighted aggregation**.

This produces one consistent district-level rainfall time series for Rusizi.

As part of dashboard validation, PostgreSQL returned a historical mean dekadal rainfall of approximately:

**Rusizi: 40.82 mm**

---

## Dashboard Page 4 — Extreme & Decision Support

![Extreme Rainfall Decision Support](dashboard/exports/04_Extreme_Decision_Support.png)

This page investigates unusually high district-level rainfall observations.

The analytical threshold is based on the **99th percentile of the dashboard's district-level rainfall observations**.

### Extreme Rainfall Indicators

- **Extreme rainfall threshold:** 103.00 mm
- **Observations exceeding threshold:** 487
- Extreme observations are analyzed by year and district
- Districts are compared by both extreme-event frequency and maximum observed rainfall

This page supports **screening-level investigation** of locations and periods that may deserve closer hydrological or infrastructure analysis.

An "extreme rainfall observation" in this project means a rainfall observation exceeding the defined statistical threshold. It does **not** represent a documented flood disaster.

Dekadal rainfall should also not be interpreted as infrastructure design rainfall. Flood-frequency analysis, IDF curves, drainage design, and return-period estimation require rainfall data at appropriate temporal resolutions together with additional hydrological information.

---

## Dashboard Validation

The Power BI dashboard was independently checked against the PostgreSQL analytical layer.

| Indicator | PostgreSQL Validation |
|---|---:|
| Historical annual baseline | **1,130.36 mm/year** |
| Wettest year | **2018** |
| Wettest annual rainfall | **1,365.46 mm** |
| Driest year | **2000** |
| Driest annual rainfall | **909.01 mm** |
| Extreme rainfall observations | **487** |
| Extreme rainfall threshold | **103.00 mm** |
| Rusizi mean dekadal rainfall | **40.82 mm** |

These checks confirm that the principal Power BI indicators are consistent with the PostgreSQL analytical views used as the dashboard data source.

### Dashboard Outputs

```text
dashboard/
├── Rwanda_Rainfall_Intelligence.pbix
└── exports/
    ├── Rwanda_Rainfall_Intelligence_Dashboard.pdf
    ├── 01_Rainfall_Overview.png
    ├── 02_Trends_Seasonality.png
    ├── 03_District_Intelligence.png
    └── 04_Extreme_Decision_Support.png
```

---

## Phase 7 — GIS & Spatial Rainfall Intelligence

Phase 7 transformed processed rainfall data into geographic rainfall intelligence using **QGIS and Rwanda administrative boundaries**.

Rainfall statistics were connected to Rwanda's **30 districts** through administrative PCODEs.

### District Mean Rainfall Map

![Mean Rainfall by District, Rwanda (1981–2026)](gis/outputs/Rwanda_District_Mean_Rainfall_Final.png)

The final choropleth map represents historical mean rainfall by district using five **Natural Breaks (Jenks)** classes.

The resulting spatial pattern indicates generally higher mean rainfall in western and southwestern Rwanda and lower mean-rainfall classes across several eastern districts.

### GIS Workflow

```text
Cleaned Rainfall Data
        ↓
District-Level Filtering
        ↓
PCODE / Date Aggregation
        ↓
Pixel-Weighted Aggregation
        ↓
GIS-Ready District Summary
        ↓
Rwanda District Boundaries
        ↓
PCODE Spatial Join
        ↓
QGIS Choropleth Map
        ↓
PDF / PNG Map Outputs
```

### Phase 7 Outputs

```text
data/processed/
└── rainfall_district_summary.csv

src/analysis/
└── prepare_gis_summary.py

gis/
├── Rwanda_Rainfall_Intelligence.qgz
└── outputs/
    ├── Rwanda_District_Mean_Rainfall_Final.pdf
    └── Rwanda_District_Mean_Rainfall_Final.png
```

---

## Phase 6 — Historical Rainfall Analysis

Phase 6 analyzed historical **final rainfall observations** to investigate rainfall patterns, variability, anomalies, extremes, and spatial differences before development of the district-level dashboard methodology.

### Key Findings

- **58,536 final observations** across **36 source administrative locations**
- Complete-year historical analysis: **1981–2025**
- April has the highest average dekadal rainfall: **57.79 mm**
- July has the lowest: **3.04 mm**
- Original Phase 6 Rwanda-wide annual baseline: approximately **1,154.11 mm/year**
- 2000 was the strongest dry anomaly: approximately **−20.13%**
- 2018 was the strongest wet anomaly: approximately **+19.95%**
- Original raw-observation 99th-percentile threshold: **102.70 mm**
- **586 raw observations** exceeded that threshold
- Extreme observations were concentrated mainly during **March–May**, particularly April, with a secondary concentration during **October–November**

### Methodology Note

Phase 6 and the Power BI dashboard intentionally represent two different analytical levels.

**Phase 6** operates on the original administrative rainfall observations.

The **dashboard analytical layer** consolidates rainfall to Rwanda's 30 districts using **pixel-weighted aggregation** before calculating national and district indicators.

Therefore, values such as:

```text
Phase 6 baseline                  ≈ 1,154.11 mm/year
Dashboard baseline               = 1,130.36 mm/year

Phase 6 extreme observations     = 586
Dashboard extreme observations   = 487
```

should not be expected to be identical.

The dashboard methodology is used for the final district-level decision-support reporting because it provides a consistent geographic analytical layer across Rwanda's 30 districts.

---

## PostgreSQL Database

Database:

```text
rwanda_rainfall
```

Main table:

```text
rainfall_observations
```

Primary key:

```text
(date, adm_id, version)
```

The database contains **58,680 observations** across final, preliminary, and forecast versions.

### Analytical Views

The dashboard uses PostgreSQL analytical views including:

```text
vw_district_rainfall
vw_district_dimension
vw_annual_rainfall
vw_annual_rainfall_anomalies
vw_monthly_seasonality
vw_extreme_rainfall_events
```

These views create a reusable analytical layer between the operational rainfall table and Power BI.

---

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

The pipeline processes **58,680 rows** using batch loading, staging tables, primary-key conflict protection, and idempotent execution.

Run with:

```bash
python src/etl/pipeline.py
```

---

## SQL Layer

```text
sql/
├── 01_create_rainfall_table.sql
├── 02_validate_rainfall_data.sql
└── 03_create_dashboard_views.sql
```

The SQL layer supports:

- Database table creation
- Data-quality validation
- Duplicate and missing-value checks
- Administrative-location validation
- District-level pixel-weighted aggregation
- Annual rainfall calculations
- Rainfall anomaly calculations
- Monthly seasonality
- Extreme rainfall identification
- Dashboard-ready analytical datasets

> `03_create_dashboard_views.sql` should contain the PostgreSQL view definitions used by Power BI so the dashboard analytical layer is reproducible.

---

## Technology Stack

**Data Engineering**
- Python
- Pandas
- PostgreSQL
- SQL
- ETL pipeline development

**Data Visualization & Business Intelligence**
- Microsoft Power BI
- DAX
- PostgreSQL analytical views

**Geospatial Analysis**
- QGIS
- GeoJSON
- ESRI Shapefile
- Rwanda administrative boundaries

**Engineering Domain**
- Water Resources Engineering
- Rainfall analysis
- Spatial rainfall intelligence
- Environmental decision support

**Development & Version Control**
- Visual Studio Code
- Git
- GitHub

---

## Project Structure

```text
Rwanda_Rainfall_intelligence/
│
├── data/
│   ├── raw/
│   │   └── rwa-rainfall-subnat-full.csv
│   │
│   ├── processed/
│   │   ├── rwanda_rainfall_cleaned.csv
│   │   ├── rainfall_yearly_anomalies.csv
│   │   ├── rainfall_extreme_events.csv
│   │   ├── rainfall_spatial_summary.csv
│   │   └── rainfall_district_summary.csv
│   │
│   └── boundaries/
│       ├── provinces/
│       └── district/
│
├── Notebooks/
│   ├── 01_data_exploration.py
│   └── 02_data_cleaning.py
│
├── src/
│   ├── analysis/
│   │   ├── rainfall_baseline.py
│   │   ├── rainfall_seasonality.py
│   │   ├── rainfall_trends.py
│   │   ├── rainfall_anomalies.py
│   │   ├── rainfall_extremes.py
│   │   ├── rainfall_spatial.py
│   │   └── prepare_gis_summary.py
│   │
│   └── etl/
│       ├── extract.py
│       ├── transform.py
│       ├── load.py
│       └── pipeline.py
│
├── gis/
│   ├── Rwanda_Rainfall_Intelligence.qgz
│   └── outputs/
│       ├── Rwanda_District_Mean_Rainfall_Final.pdf
│       └── Rwanda_District_Mean_Rainfall_Final.png
│
├── dashboard/
│   ├── Rwanda_Rainfall_Intelligence.pbix
│   └── exports/
│       ├── Rwanda_Rainfall_Intelligence_Dashboard.pdf
│       ├── 01_Rainfall_Overview.png
│       ├── 02_Trends_Seasonality.png
│       ├── 03_District_Intelligence.png
│       └── 04_Extreme_Decision_Support.png
│
├── sql/
│   ├── 01_create_rainfall_table.sql
│   ├── 02_validate_rainfall_data.sql
│   └── 03_create_dashboard_views.sql
│
├── .gitignore
├── .env
└── README.md
```

> Raw datasets, credentials, environment variables, and other sensitive or machine-specific configuration files are excluded from version control where appropriate.

---

## Project Roadmap

```text
Phase 1 — Project Setup                         ✅
Phase 2 — Data Exploration & Understanding      ✅
Phase 3 — Data Cleaning & Quality Validation    ✅
Phase 4 — Database & Data Storage               ✅
Phase 5 — ETL Pipeline                          ✅
Phase 6 — Rainfall Data Analysis                ✅
Phase 7 — GIS & Spatial Rainfall Intelligence   ✅
Phase 8 — Dashboard & Decision Support          ✅
Phase 9 — Productionization & Portfolio         → NEXT
```

---

## Future Development

Phase 9 will focus on strengthening the project as a production-oriented data engineering portfolio system.

Potential extensions include:

- PostGIS spatial database integration
- GeoPandas geospatial processing
- Automated data-quality monitoring
- Apache Airflow workflow orchestration
- Apache Kafka streaming ingestion
- Docker containerization
- Automated pipeline scheduling
- Additional rainfall and hydrological datasets
- Rainfall forecasting and advanced hydrological analysis

These components will be added where they provide genuine engineering value rather than simply increasing the number of technologies used.

---

## Project Vision

Rwanda Rainfall Intelligence is being developed toward a **water and environmental data intelligence platform** combining data engineering, rainfall analysis, geospatial information, database systems, and interactive decision-support tools.

The long-term objective is to demonstrate how modern data engineering can support practical applications in **water resources, environmental monitoring, infrastructure planning, and climate-related analysis**.

---

## Author

**GATERA Emile**

**Civil & Data Water Engineer**

Civil & Water Resources Engineering | Data Engineering | GIS | Water Data Intelligence


