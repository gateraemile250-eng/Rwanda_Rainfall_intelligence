CREATE OR REPLACE VIEW vw_district_rainfall AS
SELECT
    date,
    pcode,
    version,
    SUM(n_pixels) AS total_pixels,
    SUM(rfh * n_pixels) / NULLIF(SUM(n_pixels), 0) AS rainfall_mm,
    SUM(rfh_avg * n_pixels) / NULLIF(SUM(n_pixels), 0) AS long_term_avg_mm
FROM rainfall_observations
WHERE adm_level = 2
  AND version = 'final'
GROUP BY date, pcode, version;


CREATE OR REPLACE VIEW vw_annual_rainfall AS
WITH national_dekadal AS (
    SELECT
        date,
        SUM(rainfall_mm * total_pixels)
        / NULLIF(SUM(total_pixels), 0) AS national_rainfall_mm
    FROM vw_district_rainfall
    GROUP BY date
)
SELECT
    EXTRACT(YEAR FROM date)::integer AS year,
    SUM(national_rainfall_mm) AS annual_rainfall_mm
FROM national_dekadal
WHERE EXTRACT(YEAR FROM date) BETWEEN 1981 AND 2025
GROUP BY EXTRACT(YEAR FROM date)
ORDER BY year;


CREATE OR REPLACE VIEW vw_annual_rainfall_anomalies AS
WITH baseline AS (
    SELECT AVG(annual_rainfall_mm) AS baseline_mm
    FROM vw_annual_rainfall
)
SELECT
    a.year,
    a.annual_rainfall_mm,
    b.baseline_mm,
    a.annual_rainfall_mm - b.baseline_mm AS anomaly_mm,
    ((a.annual_rainfall_mm - b.baseline_mm)
        / NULLIF(b.baseline_mm, 0)) * 100 AS anomaly_percent
FROM vw_annual_rainfall AS a
CROSS JOIN baseline AS b
ORDER BY a.year;


CREATE OR REPLACE VIEW vw_monthly_seasonality AS
WITH national_dekadal AS (
    SELECT
        date,
        SUM(rainfall_mm * total_pixels)
        / NULLIF(SUM(total_pixels), 0) AS national_rainfall_mm
    FROM vw_district_rainfall
    WHERE EXTRACT(YEAR FROM date) BETWEEN 1981 AND 2025
    GROUP BY date
),
monthly_totals AS (
    SELECT
        EXTRACT(YEAR FROM date)::integer AS year,
        EXTRACT(MONTH FROM date)::integer AS month_number,
        SUM(national_rainfall_mm) AS monthly_rainfall_mm
    FROM national_dekadal
    GROUP BY
        EXTRACT(YEAR FROM date),
        EXTRACT(MONTH FROM date)
)
SELECT
    month_number,
    TO_CHAR(
        MAKE_DATE(2000, month_number, 1),
        'FMMonth'
    ) AS month_name,
    AVG(monthly_rainfall_mm) AS historical_mean_monthly_rainfall_mm
FROM monthly_totals
GROUP BY month_number
ORDER BY month_number;


CREATE OR REPLACE VIEW vw_district_dimension AS
SELECT *
FROM (
    VALUES
        ('RW11', 'Nyarugenge', 'Kigali'),
        ('RW12', 'Gasabo', 'Kigali'),
        ('RW13', 'Kicukiro', 'Kigali'),

        ('RW21', 'Nyanza', 'South'),
        ('RW22', 'Gisagara', 'South'),
        ('RW23', 'Nyaruguru', 'South'),
        ('RW24', 'Huye', 'South'),
        ('RW25', 'Nyamagabe', 'South'),
        ('RW26', 'Ruhango', 'South'),
        ('RW27', 'Muhanga', 'South'),
        ('RW28', 'Kamonyi', 'South'),

        ('RW31', 'Karongi', 'West'),
        ('RW32', 'Rutsiro', 'West'),
        ('RW33', 'Rubavu', 'West'),
        ('RW34', 'Nyabihu', 'West'),
        ('RW35', 'Ngororero', 'West'),
        ('RW36', 'Rusizi', 'West'),
        ('RW37', 'Nyamasheke', 'West'),

        ('RW41', 'Rulindo', 'North'),
        ('RW42', 'Gakenke', 'North'),
        ('RW43', 'Musanze', 'North'),
        ('RW44', 'Burera', 'North'),
        ('RW45', 'Gicumbi', 'North'),

        ('RW51', 'Rwamagana', 'East'),
        ('RW52', 'Nyagatare', 'East'),
        ('RW53', 'Gatsibo', 'East'),
        ('RW54', 'Kayonza', 'East'),
        ('RW55', 'Kirehe', 'East'),
        ('RW56', 'Ngoma', 'East'),
        ('RW57', 'Bugesera', 'East')
) AS districts(pcode, district_name, province);


CREATE OR REPLACE VIEW vw_extreme_rainfall_events AS
WITH historical_rainfall AS (
    SELECT
        date,
        pcode,
        rainfall_mm
    FROM vw_district_rainfall
    WHERE EXTRACT(YEAR FROM date) BETWEEN 1981 AND 2025
      AND rainfall_mm IS NOT NULL
),
extreme_threshold AS (
    SELECT
        percentile_cont(0.99)
        WITHIN GROUP (ORDER BY rainfall_mm) AS threshold_mm
    FROM historical_rainfall
)
SELECT
    h.date,
    EXTRACT(YEAR FROM h.date)::integer AS year,
    EXTRACT(MONTH FROM h.date)::integer AS month_number,
    h.pcode,
    d.district_name,
    d.province,
    h.rainfall_mm,
    t.threshold_mm,
    h.rainfall_mm - t.threshold_mm AS exceedance_mm
FROM historical_rainfall h
CROSS JOIN extreme_threshold t
LEFT JOIN vw_district_dimension d
    ON h.pcode = d.pcode
WHERE h.rainfall_mm >= t.threshold_mm
ORDER BY h.date, h.pcode;