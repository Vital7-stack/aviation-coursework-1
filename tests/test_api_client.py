from unittest.mock import patch, Mock
from aviation.api_client import APIClient
from aviation.models import Airplane
from requests.exceptions import HTTPError


@patch("requests.get")
def test_get_airplanes_in_area(mock_get):
    mock_resp = Mock()
    mock_resp.json.return_value = {
        "states": [
            [
                "abc123", "TEST123", "Russia", 1720000000, 1720000010,
                37.6, 55.7, 10000.0, False, 250.0, 90.0, 0.0, None, 10100.0, "7000"
            ]
        ]
    }
    mock_get.return_value = mock_resp

    planes = APIClient.get_airplanes_in_area(50.0, 60.0, 30.0, 40.0)

    assert isinstance(planes, list)
    assert len(planes) == 1
    assert planes[0].icao24 == "abc123"


@patch("requests.get")
def test_get_airplanes_in_area_error_handling(mock_get):
    # Делаем так, чтобы requests.get сразу выбросил HTTPError
    mock_get.side_effect = HTTPError("HTTP Error 429")

    result = APIClient.get_airplanes_in_area(50.0, 60.0, 30.0, 40.0)

    # Главное: при ошибке должен вернуться пустой список
    assert result == []


@patch("requests.get")
def test_get_airplanes_invalid_json(mock_get):
    mock_resp = Mock()
    # Возвращаем ответ, но json() будет кидать ValueError
    mock_resp.json.side_effect = ValueError("Invalid JSON")
    mock_get.return_value = mock_resp

    result = APIClient.get_airplanes_in_area(50.0, 60.0, 30.0, 40.0)
    assert result == []