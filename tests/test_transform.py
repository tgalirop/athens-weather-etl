from decimal import Decimal

import pytest

from weather_etl.transform import DataQualityError, transform


def valid_payload() -> dict:
    return {
        "hourly": {
            "time": ["2026-07-27T09:00", "2026-07-27T10:00"],
            "temperature_2m": [29.4, 30.1],
            "relative_humidity_2m": [48, 45],
            "precipitation": [0.0, 0.2],
            "wind_speed_10m": [8.5, 10.2],
            "weather_code": [0, 1],
        }
    }


def test_transform_returns_typed_records() -> None:
    records = transform(valid_payload(), "Athens")

    assert len(records) == 2
    assert records[0].location_name == "Athens"
    assert records[0].temperature_c == Decimal("29.4")
    assert records[1].precipitation_mm == Decimal("0.2")


def test_transform_rejects_mismatched_array_lengths() -> None:
    payload = valid_payload()
    payload["hourly"]["temperature_2m"] = [29.4]

    with pytest.raises(DataQualityError, match="different lengths"):
        transform(payload, "Athens")


def test_transform_rejects_invalid_humidity() -> None:
    payload = valid_payload()
    payload["hourly"]["relative_humidity_2m"][0] = 140

    with pytest.raises(DataQualityError, match="Invalid humidity"):
        transform(payload, "Athens")


def test_transform_rejects_negative_precipitation() -> None:
    payload = valid_payload()
    payload["hourly"]["precipitation"][0] = -1

    with pytest.raises(DataQualityError, match="Negative precipitation"):
        transform(payload, "Athens")
