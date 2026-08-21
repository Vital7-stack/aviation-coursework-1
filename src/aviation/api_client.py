import requests
from typing import List, Optional
from .models import Country, Airplane


class APIClient:
    @staticmethod
    def get_country_coordinates(country_name: str) -> Optional[Country]:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": country_name, "format": "json", "limit": 1}

        # Обязательно нужен User-Agent, иначе 403
        headers = {
            "User-Agent": "aviation-coursework-1/1.0 (vital7-stack@github.com)"
        }

        try:
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except (requests.exceptions.RequestException, ValueError):
            return None

        if not data:
            return None
        item = data[0]
        return Country(
            name=country_name,
            country_code=None,
            latitude=float(item["lat"]),
            longitude=float(item["lon"]),
        )

    @staticmethod
    def get_airplanes_in_area(
            min_lat: float, max_lat: float, min_lon: float, max_lon: float
    ) -> List[Airplane]:
        url = "https://opensky-network.org/api/states/all"
        params = {
            "lamin": min_lat,
            "lamax": max_lat,
            "lomin": min_lon,
            "lomax": max_lon,
        }
        try:
            resp = requests.get(url, params=params, timeout=30)
            data = resp.json()
        except (requests.exceptions.HTTPError, ValueError, requests.exceptions.RequestException):
            return []

        states = data.get("states")
        if not states:
            return []

        planes = []
        for s in states:
            if len(s) < 15:
                continue

            # --- ГЛАВНОЕ ИСПРАВЛЕНИЕ: приводим типы вручную ---
            # on_ground и spi в API приходят как 0/1 (числа), а в БД нужны True/False
            on_ground_val = s[8]
            spi_val = s[13]

            planes.append(Airplane(
                icao24=s[0] or "",
                callsign=s[1],
                origin_country=s[2],
                time_position=s[3],
                last_seen=s[4],
                longitude=s[5],
                latitude=s[6],
                baro_altitude=s[7],
                on_ground=bool(on_ground_val) if on_ground_val is not None else None,
                velocity=s[9],
                true_track=s[10],
                vertical_rate=s[11],
                squawk=s[12],
                spi=bool(spi_val) if spi_val is not None else None,
                geo_altitude=s[14],
            ))
        return planes