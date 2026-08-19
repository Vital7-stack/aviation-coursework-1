from unittest.mock import patch, Mock
import pytest
from requests.exceptions import RequestException
from aviation.api_client import APIClient


@patch("requests.get")
def test_get_airplanes_in_area(mock_get):
    """
    Проверяет, что get_airplanes_in_area корректно обрабатывает ответ OpenSky.
    ВАЖНО: OpenSky возвращает states как список СПИСКОВ, а не словарей.
    Наш метод парсит именно по индексам, поэтому мок должен быть в таком же формате.
    """
    mock_resp = Mock()
    # Это тот формат, который реально приходит от OpenSky API
    mock_resp.json.return_value = {
        "states": [
            [
                "abc123",  # icao24 (s[0])
                "TEST123",  # callsign (s[1])
                "Russia",  # origin_country (s[2])
                1720000000,  # time_position (s[3])
                1720000010,  # last_seen (s[4])
                37.6,  # longitude (s[5])
                55.7,  # latitude (s[6])
                10000.0,  # baro_altitude (s[7])
                False,  # on_ground (s[8])
                250.0,  # velocity (s[9])
                90.0,  # true_track (s[10])
                0.0,  # vertical_rate (s[11])
                None,  # (пропущенный элемент, чтобы сдвинуть индексы)
                10100.0,  # geo_altitude (s[13])
                "7000"  # squawk (s[14])
            ]
        ]
    }
    mock_get.return_value = mock_resp

    planes = APIClient.get_airplanes_in_area(50.0, 60.0, 30.0, 40.0)

    assert isinstance(planes, list)
    assert len(planes) == 1, f"Ожидается 1 самолёт, а получено {len(planes)}"
    assert planes[0]["icao24"] == "abc123"
    assert planes[0]["velocity"] == 250.0
    assert "callsign" in planes[0]
    assert "origin_country" in planes[0]


@patch("requests.get")
def test_get_airplanes_in_area_error_handling(mock_get):
    """
    Проверяет обработку ошибок API.
    Теперь код явно оборачивает ошибки в RuntimeError.
    """
    # Сценарий 1: HTTP-ошибка (не 200 OK)
    mock_resp_error = Mock()
    mock_resp_error.status_code = 429
    mock_resp_error.raise_for_status.side_effect = Exception("HTTP Error 429")
    mock_get.return_value = mock_resp_error

    # Ловим RuntimeError, который ты теперь выбрасываешь в api_client.py
    with pytest.raises(RuntimeError):
        APIClient.get_airplanes_in_area(50.0, 60.0, 30.0, 40.0)

    # Сценарий 2: Ошибка сети (таймаут)
    mock_get.side_effect = RequestException("Connection timeout")

    # И здесь тоже ловим RuntimeError — твой try/except превратит таймаут в RuntimeError
    with pytest.raises(RuntimeError):
        APIClient.get_airplanes_in_area(50.0, 60.0, 30.0, 40.0)