from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from weather_etl.models import WeatherRecord

REQUIRED_HOURLY_FIELDS = (
    "time",
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
    "weather_code",
)


class DataQualityError(ValueError):
    """Raised when extracted data violates an expected quality rule."""


def _decimal(value: Any, field: str) -> Decimal:
    if value is None:
        raise DataQualityError(f"{field} contains a null value")
    return Decimal(str(value))


def transform(payload: dict[str, Any], location_name: str) -> list[WeatherRecord]:
    hourly = payload.get("hourly")
    if not isinstance(hourly, dict):
        raise DataQualityError("Missing or invalid 'hourly' object")

    missing = [field for field in REQUIRED_HOURLY_FIELDS if field not in hourly]
    if missing:
        raise DataQualityError(f"Missing hourly fields: {', '.join(missing)}")

    lengths = {field: len(hourly[field]) for field in REQUIRED_HOURLY_FIELDS}
    if len(set(lengths.values())) != 1:
        raise DataQualityError(f"Hourly arrays have different lengths: {lengths}")

    records: list[WeatherRecord] = []
    for index, timestamp in enumerate(hourly["time"]):
        humidity = hourly["relative_humidity_2m"][index]
        precipitation = _decimal(hourly["precipitation"][index], "precipitation")

        if humidity is None or not 0 <= int(humidity) <= 100:
            raise DataQualityError(f"Invalid humidity at index {index}: {humidity}")
        if precipitation < 0:
            raise DataQualityError(f"Negative precipitation at index {index}")

        records.append(
            WeatherRecord(
                location_name=location_name,
                observed_at=datetime.fromisoformat(timestamp),
                temperature_c=_decimal(
                    hourly["temperature_2m"][index], "temperature_2m"
                ),
                relative_humidity_pct=int(humidity),
                precipitation_mm=precipitation,
                wind_speed_kmh=_decimal(hourly["wind_speed_10m"][index], "wind_speed_10m"),
                weather_code=int(hourly["weather_code"][index]),
                source="open-meteo",
            )
        )

    if not records:
        raise DataQualityError("The source returned zero records")

    return records
