import requests
from typing import List, Dict, Any, Optional
from .config import OPENSKY_URL, NOMINATIM_URL, USER_AGENT


class APIClient:
    """
    Клиент для работы с внешними API: Nominatim и OpenSky.
    Отвечает за получение координат стран и текущих состояний самолётов.
    """

    @staticmethod
    def get_country_coordinates(country_name: str) -> Optional[Dict[str, float]]:
        """
        Получить координаты центра страны через Nominatim.

        :param country_name: Название страны.
        :return: Словарь с latitude и longitude или None, если страна не найдена.
        """
        params = {
            "q": country_name,
            "format": "json",
            "limit": 1,
        }
        headers = {"User-Agent": USER_AGENT}

        try:
            resp = requests.get(
                NOMINATIM_URL,
                params=params,
                headers=headers,
                timeout=10,
            )
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Ошибка Nominatim для '{country_name}': {e}")
            return None

        data = resp.json()
        if not data:
            return None

        item = data[0]
        return {
            "latitude": float(item["lat"]),
            "longitude": float(item["lon"]),
        }

    @staticmethod
    def get_airplanes_in_area(
            min_lat: float,
            max_lat: float,
            min_lon: float,
            max_lon: float,
    ) -> List[Dict[str, Any]]:
        params = {
            "lamin": min_lat,
            "lamax": max_lat,
            "lomin": min_lon,
            "lomax": max_lon,
        }
        headers = {"User-Agent": USER_AGENT}

        try:
            resp = requests.get(
                OPENSKY_URL,
                params=params,
                headers=headers,
                timeout=30,
            )
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Ошибка OpenSky API: {e}")
            return []

        # OpenSky states/all сразу отдаёт список, без обертки {"states": [...]}
        data = resp.json()
        if not isinstance(data, list):
            return []
        return data