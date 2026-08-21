import pytest
from aviation.models import Country, Airplane

def test_insert_countries(db):
    countries = [
        Country(name="Russia", latitude=55.7558, longitude=37.6176),
        Country(name="Germany", latitude=52.5200, longitude=13.4050),
        Country(name="France", latitude=48.8566, longitude=2.3522),
        Country(name="Japan", latitude=35.6762, longitude=139.6503),
        Country(name="Brazil", latitude=-15.7797, longitude=-47.9167),
        Country(name="Canada", latitude=45.4215, longitude=-75.6972),
        Country(name="Australia", latitude=-35.2809, longitude=149.1300),
        Country(name="India", latitude=28.7041, longitude=77.1025),
        Country(name="Spain", latitude=40.4168, longitude=-3.7038),
        Country(name="Italy", latitude=41.9029, longitude=12.4933),
    ]

    db.insert_countries(countries)

    with db.conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM countries")
        count = cur.fetchone()[0]
    assert count >= 10


def test_insert_airplanes_full_data(db):
    planes = [
        Airplane(
            icao24="abc123", callsign="TEST123", origin_country="Russia",
            last_seen=1720000000, longitude=37.6, latitude=55.7,
            baro_altitude=10000.0, on_ground=False, velocity=250.0,
            true_track=90.0, vertical_rate=0.0, squawk="7000", spi=None, geo_altitude=10100.0
        ),
        Airplane(
            icao24="def456", callsign="TEST456", origin_country="Germany",
            last_seen=1720000010, longitude=13.4, latitude=52.5,
            baro_altitude=11000.0, on_ground=False, velocity=300.0,
            true_track=180.0, vertical_rate=5.0, squawk="7100", spi=None, geo_altitude=11100.0
        )
    ]
    db.insert_airplanes(planes)

    with db.conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM airplanes")
        count = cur.fetchone()[0]
    assert count >= 2


def test_get_avg_speed_and_higher(db):
    # Сначала вставим тестовые самолёты
    planes = [
        Airplane(icao24="p1", velocity=100.0, callsign="A", origin_country="X",
                 last_seen=0, longitude=0.0, latitude=0.0, baro_altitude=None,
                 on_ground=False, true_track=0.0, vertical_rate=0.0,
                 squawk="0000", spi=None, geo_altitude=0.0),
        Airplane(icao24="p2", velocity=200.0, callsign="B", origin_country="X",
                 last_seen=0, longitude=0.0, latitude=0.0, baro_altitude=None,
                 on_ground=False, true_track=0.0, vertical_rate=0.0,
                 squawk="0000", spi=None, geo_altitude=0.0),
        Airplane(icao24="p3", velocity=300.0, callsign="C", origin_country="X",
                 last_seen=0, longitude=0.0, latitude=0.0, baro_altitude=None,
                 on_ground=False, true_track=0.0, vertical_rate=0.0,
                 squawk="0000", spi=None, geo_altitude=0.0),
    ]
    db.insert_airplanes(planes)

    avg = db.get_avg_speed()
    assert avg == 200.0  # (100 + 200 + 300) / 3

    faster = db.get_aeroplanes_with_higher_speed()
    # Должен быть только p3 (300 > 200)
    assert len(faster) == 1
    assert faster[0]["icao24"] == "p3"


def test_get_aeroplanes_with_keyword(db):
    planes = [
        Airplane(icao24="x1", callsign="ACA123", origin_country="Y",
                 last_seen=0, longitude=0.0, latitude=0.0, baro_altitude=None,
                 on_ground=False, velocity=0.0, true_track=0.0, vertical_rate=0.0,
                 squawk="0000", spi=None, geo_altitude=0.0),
        Airplane(icao24="x2", callsign="XYZ999", origin_country="Y",
                 last_seen=0, longitude=0.0, latitude=0.0, baro_altitude=None,
                 on_ground=False, velocity=0.0, true_track=0.0, vertical_rate=0.0,
                 squawk="0000", spi=None, geo_altitude=0.0),
    ]
    db.insert_airplanes(planes)

    result = db.get_aeroplanes_with_keyword("ACA")
    assert len(result) == 1
    assert result[0]["icao24"] == "x1"