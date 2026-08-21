from dataclasses import dataclass

@dataclass
class Country:
    name: str
    country_code: str | None = None
    latitude: float | None = None
    longitude: float | None = None

@dataclass
class Airplane:
    icao24: str
    callsign: str | None = None
    origin_country: str | None = None
    time_position: float | None = None
    last_seen: float | None = None
    longitude: float | None = None
    latitude: float | None = None
    baro_altitude: float | None = None
    on_ground: bool | None = None
    velocity: float | None = None
    true_track: float | None = None
    vertical_rate: float | None = None
    squawk: str | None = None
    spi: bool | None = None
    geo_altitude: float | None = None
