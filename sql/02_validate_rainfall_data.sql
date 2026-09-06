-- ============================================================
-- Rwanda Rainfall Intelligence
-- PostgreSQL Data Validation Queries
-- ============================================================


-- 1. Total number of records
-- Confirms that the expected number of observations were loaded.

SELECT COUNT(*) AS total_rows
FROM rainfall_observations;


-- 2. Date coverage
-- Confirms the earliest and latest observation dates.

SELECT
    MIN(date) AS earliest_date,
    MAX(date) AS latest_date
FROM rainfall_observations;


-- 3. Number of unique dates and administrative locations
-- Confirms the overall dataset coverage.

SELECT
    COUNT(DISTINCT date) AS unique_dates,
    COUNT(DISTINCT adm_id) AS unique_locations
FROM rainfall_observations;


-- 4. Duplicate primary-key combinations
-- Checks whether (date, adm_id, version) is truly unique.

SELECT
    date,
    adm_id,
    version,
    COUNT(*) AS duplicate_count
FROM rainfall_observations
GROUP BY date, adm_id, version
HAVING COUNT(*) > 1;


-- 5. Missing rainfall observations
-- rfh is the main rainfall observation variable.

SELECT
    COUNT(*) AS total_rows,
    COUNT(rfh) AS rfh_available,
    COUNT(*) - COUNT(rfh) AS rfh_missing
FROM rainfall_observations;


-- 6. Missing values across rainfall variables
-- Identifies missing values in the rainfall and accumulation fields.

SELECT
    COUNT(*) - COUNT(rfh) AS rfh_missing,
    COUNT(*) - COUNT(rfh_avg) AS rfh_avg_missing,
    COUNT(*) - COUNT(r1h) AS r1h_missing,
    COUNT(*) - COUNT(r1h_avg) AS r1h_avg_missing,
    COUNT(*) - COUNT(r3h) AS r3h_missing,
    COUNT(*) - COUNT(r3h_avg) AS r3h_avg_missing,
    COUNT(*) - COUNT(rfq) AS rfq_missing,
    COUNT(*) - COUNT(r1q) AS r1q_missing,
    COUNT(*) - COUNT(r3q) AS r3q_missing
FROM rainfall_observations;


-- 7. Negative rainfall values
-- Rainfall measurements should not be negative.

SELECT COUNT(*) AS negative_rainfall_values
FROM rainfall_observations
WHERE rfh < 0
   OR rfh_avg < 0
   OR r1h < 0
   OR r1h_avg < 0
   OR r3h < 0
   OR r3h_avg < 0;


-- 8. Invalid pixel counts
-- n_pixels must be greater than zero.

SELECT COUNT(*) AS invalid_pixel_counts
FROM rainfall_observations
WHERE n_pixels <= 0
   OR n_pixels IS NULL;


-- 9. Rainfall accumulation consistency
-- Checks that shorter accumulation periods do not exceed longer periods.

SELECT COUNT(*) AS inconsistent_r1h
FROM rainfall_observations
WHERE r1h IS NOT NULL
  AND rfh IS NOT NULL
  AND r1h < rfh;


SELECT COUNT(*) AS inconsistent_r3h
FROM rainfall_observations
WHERE r3h IS NOT NULL
  AND r1h IS NOT NULL
  AND r3h < r1h;


-- 10. Average accumulation consistency
-- Checks the same relationship for long-term average rainfall.

SELECT
    COUNT(*) FILTER (
        WHERE r1h_avg IS NOT NULL
          AND rfh_avg IS NOT NULL
          AND r1h_avg < rfh_avg
    ) AS r1h_avg_less_than_rfh_avg,

    COUNT(*) FILTER (
        WHERE r3h_avg IS NOT NULL
          AND r1h_avg IS NOT NULL
          AND r3h_avg < r1h_avg
    ) AS r3h_avg_less_than_r1h_avg
FROM rainfall_observations;


-- 11. Administrative level distribution
-- Shows how observations are distributed across administrative levels.

SELECT
    adm_level,
    COUNT(*) AS row_count
FROM rainfall_observations
GROUP BY adm_level
ORDER BY adm_level;


-- 12. Dataset version distribution
-- Confirms the presence of final, preliminary, and forecast records.

SELECT
    version,
    COUNT(*) AS row_count
FROM rainfall_observations
GROUP BY version
ORDER BY version;


-- 13. Date coverage by administrative location
-- Confirms that every location has the expected number of dates.

SELECT
    adm_id,
    COUNT(DISTINCT date) AS number_of_dates,
    MIN(date) AS first_date,
    MAX(date) AS last_date
FROM rainfall_observations
GROUP BY adm_id
ORDER BY adm_id;


-- 14. Final overall validation summary
-- Provides the main quality indicators in one result.

SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT date) AS unique_dates,
    COUNT(DISTINCT adm_id) AS unique_locations,
    COUNT(DISTINCT pcode) AS unique_pcodes,

    COUNT(*) FILTER (WHERE rfh IS NULL) AS missing_rfh,

    COUNT(*) FILTER (WHERE rfh < 0) AS negative_rfh,

    COUNT(*) FILTER (
        WHERE n_pixels <= 0 OR n_pixels IS NULL
    ) AS invalid_pixel_counts,

    COUNT(*) FILTER (WHERE version = 'final') AS final_rows,
    COUNT(*) FILTER (WHERE version = 'prelim') AS prelim_rows,
    COUNT(*) FILTER (WHERE version = 'forecast') AS forecast_rows

FROM rainfall_observations;