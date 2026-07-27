\echo '1) Latest 10 weather records'
SELECT
    location_name,
    observed_at,
    temperature_c,
    relative_humidity_pct,
    precipitation_mm,
    wind_speed_kmh
FROM weather_hourly
ORDER BY observed_at DESC
LIMIT 10;

\echo '2) Daily aggregates'
SELECT
    location_name,
    observed_at::date AS weather_date,
    ROUND(AVG(temperature_c), 2) AS avg_temperature_c,
    MIN(temperature_c) AS min_temperature_c,
    MAX(temperature_c) AS max_temperature_c,
    SUM(precipitation_mm) AS total_precipitation_mm
FROM weather_hourly
GROUP BY location_name, observed_at::date
ORDER BY weather_date;

\echo '3) Wettest hour per day using a window function'
WITH ranked_hours AS (
    SELECT
        location_name,
        observed_at,
        precipitation_mm,
        ROW_NUMBER() OVER (
            PARTITION BY location_name, observed_at::date
            ORDER BY precipitation_mm DESC, observed_at
        ) AS row_num
    FROM weather_hourly
)
SELECT location_name, observed_at, precipitation_mm
FROM ranked_hours
WHERE row_num = 1
ORDER BY observed_at;

\echo '4) ETL execution history'
SELECT
    run_id,
    source_mode,
    status,
    records_processed,
    started_at,
    finished_at,
    finished_at - started_at AS duration
FROM etl_runs
ORDER BY started_at DESC
LIMIT 10;
