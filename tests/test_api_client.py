import pytest
from unittest.mock import patch, Mock
from aviation.api_client import APIClient

@patch("requests.get")
def test_get_country_coordinates(mock_get):
    # Мок ответа Nominatim
    mock_resp = Mock()
    mock_resp.json.return_value = [
        {"lat": "55.7558", "lon": "37.6176"}
    ]
    mock_get.return_value = mock_resp

    result = APIClient.get_country_coordinates("Russia")
    assert result is not None
    assert result["latitude"] == 55.7558
    assert result["longitude"] == 37.6176

@patch("requests.get")
def test_get_country_coordinates_not_found(mock_get):
    mock_resp = Mock()
    mock_resp.json.return_value = []
    mock_get.return_value = mock_resp

    result = APIClient.get_country_coordinates("NonexistentCountry123")
    assert result is None

@patch("requests.get")
def test_get_airplanes_in_area(mock_get):
    mock_resp = Mock()
    mock_resp.json.return_value = [
        {
            "icao24": "abc123",
            "callsign": "TEST123",
            "origin_country": "Russia",
            "time_position": 1720000000,
            "last_seen": 1720000010,
            "longitude": 37.6,
            "latitude": 55.7,
            "velocity": 250.0,
        }
    ]
    mock_get.return_value = mock_resp

    planes = APIClient.get_airplanes_in_area(50.0, 60.0, 30.0, 40.0)
    assert len(planes) == 1
    assert planes[0]["icao24"] == "abc123"