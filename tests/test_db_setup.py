from aviation.models import Country, Airplane

def test_tables_exist_and_insert_works(db):
    # 1. Вставляем тестовые страны
    countries = [
        Country(name="TestCountry1", latitude=50.0, longitude=30.0),
        Country(name="TestCountry2", latitude=51.0, longitude=31.0),
    ]
    db.insert_countries(countries)

    with db.conn.cursor() as cur:
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
              AND table_name IN ('countries', 'airplanes');
        """)
        tables = {row[0] for row in cur.fetchall()}

    assert "countries" in tables
    assert "airplanes" in tables

    # 2. Вставляем тестовые самолёты (с разными скоростями, чтобы проверить AVG и фильтр)
    airplanes = [
        Airplane(icao24="A001", callsign="TEST1", velocity=100.0, latitude=50.0, longitude=30.0),
        Airplane(icao24="A002", callsign="TEST2", velocity=200.0, latitude=50.5, longitude=30.5),
        Airplane(icao24="A003", callsign="ACATEST", velocity=300.0, latitude=51.0, longitude=31.0),  # для поиска по 'ACA'
    ]
    db.insert_airplanes(airplanes)

    # 3. Проверяем аналитику
    counts = db.get_countries_and_aeroplanes_count()
    assert len(counts) >= 2, "Должны быть данные по странам"

    avg_speed = db.get_avg_speed()
    assert avg_speed is not None
    assert 150 < avg_speed < 250, "Средняя скорость должна быть между 100 и 300"

    faster = db.get_aeroplanes_with_higher_speed()
    assert len(faster) >= 1, "Должен быть хотя бы один самолёт быстрее среднего"

    aca_planes = db.get_aeroplanes_with_keyword("ACA")
    assert len(aca_planes) >= 1, "Должен найтись самолёт с 'ACA' в callsign"
    assert any(p["callsign"] and "ACA" in p["callsign"] for p in aca_planes)