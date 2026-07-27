from __future__ import annotations

import logging
from pathlib import Path
from uuid import uuid4

import psycopg

from weather_etl.config import Settings
from weather_etl.database import finish_run, initialize_schema, load_records, start_run
from weather_etl.extract import extract_live, extract_sample
from weather_etl.transform import transform

LOGGER = logging.getLogger(__name__)
PROJECT_ROOT = Path.cwd()


def run_pipeline(settings: Settings) -> int:
    run_id = uuid4()
    schema_path = PROJECT_ROOT / "sql" / "001_create_tables.sql"
    sample_path = PROJECT_ROOT / "data" / "sample_open_meteo_response.json"

    with psycopg.connect(settings.database_url) as connection:
        initialize_schema(connection, schema_path)
        start_run(connection, run_id, settings.source_mode)

        try:
            if settings.source_mode == "live":
                payload = extract_live(settings.latitude, settings.longitude)
            else:
                payload = extract_sample(sample_path)

            records = transform(payload, settings.location_name)
            processed = load_records(connection, records, run_id)
            finish_run(connection, run_id, "success", processed)
            LOGGER.info("Pipeline succeeded: run_id=%s records=%s", run_id, processed)
            return processed
        except Exception as exc:
            finish_run(connection, run_id, "failed", error_message=str(exc)[:1000])
            LOGGER.exception("Pipeline failed: run_id=%s", run_id)
            raise
