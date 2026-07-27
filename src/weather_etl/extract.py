from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import requests

LOGGER = logging.getLogger(__name__)
API_URL = "https://api.open-meteo.com/v1/forecast"


def extract_live(latitude: float, longitude: float) -> dict[str, Any]:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join(
            [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation",
                "wind_speed_10m",
                "weather_code",
            ]
        ),
        "forecast_days": 3,
        "timezone": "Europe/Athens",
    }
    LOGGER.info("Extracting live weather data from Open-Meteo")
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    payload: dict[str, Any] = response.json()
    return payload


def extract_sample(path: Path) -> dict[str, Any]:
    LOGGER.info("Extracting deterministic sample data from %s", path)
    with path.open(encoding="utf-8") as file:
        payload: dict[str, Any] = json.load(file)
    return payload
