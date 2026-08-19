import requests
from .config import  OPENSKY_URL

class APIClient:
    USER_AGENT = "aviation-coursework-py3.14/1.0 (contact: zinabir7@gmail.com)"

    @staticmethod
    def get_airplanes_in_area(min_lat, max_lat, min_lon, max_lon):
        url = OPENSKY_URL
        params = {
            "lamin": min_lat,
            "lamax": max_lat,
            "lomin": min_lon,
            "lomax": max_lon,
        }
        headers = {"User-Agent": APIClient.USER_AGENT}

        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            # Это важно: теперь эти строки реально выполняются при ошибке,
            # и coverage их засчитает. Для курсовой достаточно логировать или пробросить.
            raise RuntimeError(f"Ошибка при запросе к OpenSky API: {e}") from e

        states = data.get("states", [])
        planes = []
        for s in states:
            if len(s) < 15:
                continue
            planes.append({
                "icao24": s[0],
                "callsign": s[1],
                "origin_country": s[2],
                "time_position": s[3],
                "last_seen": s[4],
                "longitude": s[5],
                "latitude": s[6],
                "baro_altitude": s[7],
                "on_ground": s[8],
                "velocity": s[9],
                "true_track": s[10],
                "vertical_rate": s[11],
                # s[12] пропускаем (None)
                "geo_altitude": s[13],
                "squawk": s[14],
            })
        return planes