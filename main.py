import time
from aviation.api_client import APIClient
from aviation.db_manager import DBManager
from aviation.models import Country

COUNTRIES_LIST = [
    "Russia", "Germany", "France", "Italy", "Spain",
    "United Kingdom", "Poland", "Turkey", "India", "Brazil"
]
BOX_SIZE = 10.0

def get_bounding_box(lat: float, lon: float, size_deg: float) -> tuple:
    half = size_deg / 2.0
    return (lat - half, lat + half, lon - half, lon + half)

def main():
    db = DBManager()
    client = APIClient()

    db.ensure_tables_exist()
    print("✅ Таблицы проверены/созданы.")

    countries_objs = []
    for country_name in COUNTRIES_LIST:
        country_obj = client.get_country_coordinates(country_name)
        if country_obj:
            countries_objs.append(country_obj)
        else:
            print(f"⚠️ Не удалось найти координаты для: {country_name}")

    if countries_objs:
        db.insert_countries(countries_objs)
        print(f"✅ Вставлено стран: {len(countries_objs)}")
    else:
        print("❌ Не удалось получить ни одной страны. Завершаю.")
        db.close()
        return

    all_airplanes_objs = []
    for country in countries_objs:
        if not country.latitude or not country.longitude:
            continue

        min_lat, max_lat, min_lon, max_lon = get_bounding_box(
            country.latitude, country.longitude, BOX_SIZE
        )
        time.sleep(1)

        planes_objs = client.get_airplanes_in_area(min_lat, max_lat, min_lon, max_lon)
        all_airplanes_objs.extend(planes_objs)

    if all_airplanes_objs:
        db.insert_airplanes(all_airplanes_objs)
        print(f"✅ Обработано самолётов: {len(all_airplanes_objs)}")
    else:
        print("⚠️ Самолёты не получены.")

    print("\n--- Отчёты ---")
    counts = db.get_countries_and_aeroplanes_count()
    print("Количество самолётов по странам:")
    for name, count in counts:
        print(f"{name}: {count}")

    avg_speed = db.get_avg_speed()
    if avg_speed is not None:
        print(f"Средняя скорость: {avg_speed:.2f} м/с")

    faster_planes = db.get_aeroplanes_with_higher_speed()
    print(f"Самолётов со скоростью выше средней: {len(faster_planes)}")

    keyword_planes = db.get_aeroplanes_with_keyword("ACA")
    print(f"Самолёты с подстрокой 'ACA' в callsign: {len(keyword_planes)}")

    db.close()
    print("\n✅ Готово.")

if __name__ == "__main__":
    main()