from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class WeatherRecord:
    location_name: str
    observed_at: datetime
    temperature_c: Decimal
    relative_humidity_pct: int
    precipitation_mm: Decimal
    wind_speed_kmh: Decimal
    weather_code: int
    source: str
