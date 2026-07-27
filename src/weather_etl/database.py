from __future__ import annotations

from pathlib import Path
from uuid import UUID

import psycopg

from weather_etl.models import WeatherRecord


def initialize_schema(connection: psycopg.Connection, schema_path: Path) -> None:
    statements = [
        statement.strip()
        for statement in schema_path.read_text(encoding="utf-8").split(";")
        if statement.strip()
    ]
    with connection.transaction():
        for statement in statements:
            connection.execute(statement)


def start_run(connection: psycopg.Connection, run_id: UUID, source_mode: str) -> None:
    connection.execute(
        """
        INSERT INTO etl_runs (run_id, pipeline_name, source_mode, status)
        VALUES (%s, 'athens_weather_etl', %s, 'running')
        """,
        (run_id, source_mode),
    )
    connection.commit()


def load_records(
    connection: psycopg.Connection, records: list[WeatherRecord], run_id: UUID
) -> int:
    rows = [
        (
            record.location_name,
            record.observed_at,
            record.temperature_c,
            record.relative_humidity_pct,
            record.precipitation_mm,
            record.wind_speed_kmh,
            record.weather_code,
            record.source,
            run_id,
        )
        for record in records
    ]

    with connection.transaction():
        with connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO weather_hourly (
                    location_name,
                    observed_at,
                    temperature_c,
                    relative_humidity_pct,
                    precipitation_mm,
                    wind_speed_kmh,
                    weather_code,
                    source,
                    last_run_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (location_name, observed_at)
                DO UPDATE SET
                    temperature_c = EXCLUDED.temperature_c,
                    relative_humidity_pct = EXCLUDED.relative_humidity_pct,
                    precipitation_mm = EXCLUDED.precipitation_mm,
                    wind_speed_kmh = EXCLUDED.wind_speed_kmh,
                    weather_code = EXCLUDED.weather_code,
                    source = EXCLUDED.source,
                    last_run_id = EXCLUDED.last_run_id,
                    loaded_at = NOW()
                """,
                rows,
            )
    return len(rows)


def finish_run(
    connection: psycopg.Connection,
    run_id: UUID,
    status: str,
    records_processed: int = 0,
    error_message: str | None = None,
) -> None:
    connection.execute(
        """
        UPDATE etl_runs
        SET status = %s,
            records_processed = %s,
            error_message = %s,
            finished_at = NOW()
        WHERE run_id = %s
        """,
        (status, records_processed, error_message, run_id),
    )
    connection.commit()
