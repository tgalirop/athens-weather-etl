from __future__ import annotations

import argparse
import logging
import os

from weather_etl.config import Settings
from weather_etl.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Athens weather ETL pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="Extract, transform and load weather data")
    run_parser.add_argument(
        "--source",
        choices=["sample", "live"],
        help="Override SOURCE_MODE for this run",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "run" and args.source:
        os.environ["SOURCE_MODE"] = args.source

    settings = Settings.from_env()
    logging.basicConfig(
        level=getattr(logging, settings.log_level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    processed = run_pipeline(settings)
    print(f"ETL completed successfully. Processed {processed} records.")


if __name__ == "__main__":
    main()
