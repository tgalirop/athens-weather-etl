from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    database_url: str
    source_mode: str
    location_name: str
    latitude: float
    longitude: float
    log_level: str

    @classmethod
    def from_env(cls) -> "Settings":
        source_mode = os.getenv("SOURCE_MODE", "sample").lower()
        if source_mode not in {"sample", "live"}:
            raise ValueError("SOURCE_MODE must be either 'sample' or 'live'")

        return cls(
            database_url=os.getenv(
                "DATABASE_URL", "postgresql://weather:weather@localhost:5432/weather"
            ),
            source_mode=source_mode,
            location_name=os.getenv("LOCATION_NAME", "Athens"),
            latitude=float(os.getenv("LATITUDE", "37.9838")),
            longitude=float(os.getenv("LONGITUDE", "23.7275")),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        )
