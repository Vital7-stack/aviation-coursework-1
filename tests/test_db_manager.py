from aviation.models import Country, Airplane

def test_insert_countries(db):
    countries = [
        Country(name="Russia", latitude=55.7558, longitude=37.6176),
        Country(name="Germany", latitude=52.5200, longitude=13.4050),
    ]
    db.insert_countries(countries)

    counts = db.get_countries_and_aeroplanes_count()
    assert len(counts) >= 2

def test_insert_airplanes(db):
    airplanes = [
        Airplane(
            icao24="abc123",
            callsign="TEST123",
            origin_country="Russia",
            velocity=250.0,
            latitude=55.7,
            longitude=37.6,
        ),
        Airplane(
            icao24="def456",
            callsign="TEST456",
            origin_country="Germany",
            velocity=300.0,
            latitude=52.5,
            longitude=13.4,
        ),
    ]
    db.insert_airplanes(airplanes)

    all_planes = db.get_all_aeroplanes()
    assert len(all_planes) == 2

def test_avg_speed(db):
    airplanes = [
        Airplane(icao24="a1", velocity=200.0),
        Airplane(icao24="a2", velocity=300.0),
    ]
    db.insert_airplanes(airplanes)
    avg = db.get_avg_speed()
    assert avg == 250.0

def test_higher_than_avg(db):
    airplanes = [
        Airplane(icao24="a1", velocity=100.0),
        Airplane(icao24="a2", velocity=200.0),
        Airplane(icao24="a3", velocity=300.0),
    ]
    db.insert_airplanes(airplanes)
    faster = db.get_aeroplanes_with_higher_speed()
    assert len(faster) == 1  # только 300 выше среднего (200)

def test_keyword_search(db):
    airplanes = [
        Airplane(icao24="x1", callsign="ACA123"),
        Airplane(icao24="x2", callsign="XYZ789"),
    ]
    db.insert_airplanes(airplanes)
    results = db.get_aeroplanes_with_keyword("ACA")
    assert len(results) == 1
    assert results[0]["callsign"] == "ACA123"