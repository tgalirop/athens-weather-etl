CREATE TABLE IF NOT EXISTS etl_runs (
    run_id UUID PRIMARY KEY,
    pipeline_name TEXT NOT NULL,
    source_mode TEXT NOT NULL CHECK (source_mode IN ('sample', 'live')),
    status TEXT NOT NULL CHECK (status IN ('running', 'success', 'failed')),
    records_processed INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS weather_hourly (
    location_name TEXT NOT NULL,
    observed_at TIMESTAMP NOT NULL,
    temperature_c NUMERIC(5, 2) NOT NULL,
    relative_humidity_pct SMALLINT NOT NULL CHECK (relative_humidity_pct BETWEEN 0 AND 100),
    precipitation_mm NUMERIC(7, 2) NOT NULL CHECK (precipitation_mm >= 0),
    wind_speed_kmh NUMERIC(6, 2) NOT NULL CHECK (wind_speed_kmh >= 0),
    weather_code SMALLINT NOT NULL,
    source TEXT NOT NULL,
    last_run_id UUID NOT NULL REFERENCES etl_runs(run_id),
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (location_name, observed_at)
);

CREATE INDEX IF NOT EXISTS idx_weather_hourly_observed_at
    ON weather_hourly (observed_at DESC);
