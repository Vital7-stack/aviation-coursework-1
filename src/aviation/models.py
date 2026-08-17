from dataclasses import dataclass
from typing import Optional

@dataclass
class Country:
    name: str
    country_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

@dataclass
class Airplane:
    icao24: str
    callsign: Optional[str] = None
    origin_country: Optional[str] = None
    time_position: Optional[float] = None
    last_seen: Optional[float] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    baro_altitude: Optional[float] = None
    on_ground: Optional[bool] = None
    velocity: Optional[float] = None
    true_track: Optional[float] = None
    vertical_rate: Optional[float] = None
    squawk: Optional[str] = None
    spi: Optional[bool] = None
    geo_altitude: Optional[float] = None
    country_id: Optional[int] = None