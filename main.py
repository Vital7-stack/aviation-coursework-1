from aviation.api_client import APIClient
from aviation.db_manager import DBManager

# Минимум 10 стран — требование критерия оценки
COUNTRIES_LIST = [
    "Russia", "Germany", "France", "Italy", "Spain",
    "United Kingdom", "Poland", "Sweden", "Norway", "Finland"
]


def main():
    client = APIClient()
    db = DBManager()

    # 1. Получаем координаты стран и сохраняем
    countries_data = []
    for name in COUNTRIES_LIST:
        coords = client.get_country_coordinates(name)
        if coords:
            countries_data.append({"name": name, **coords})
        else:
            print(f"⚠️ Не удалось получить координаты для страны: {name}")

    if len(countries_data) < 10:
        print(f"❌ Ошибка: удалось получить координаты только для {len(countries_data)} стран. Нужно минимум 10.")
        db.close()
        return

    db.insert_countries(countries_data)
    print(f"✅ Вставлено стран: {len(countries_data)}")

    # 2. Вычисляем общий bounding box по всем странам
    lats = [c["latitude"] for c in countries_data]
    lons = [c["longitude"] for c in countries_data]
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)

    print(f"🌍 Область поиска: lat [{min_lat:.2f}, {max_lat:.2f}], lon [{min_lon:.2f}, {max_lon:.2f}]")

    # 3. Получаем самолёты «прямо сейчас» в этой области
    planes = client.get_airplanes_in_area(min_lat, max_lat, min_lon, max_lon)

    if not planes:
        print("⚠️ Самолёты не получены (возможно, сейчас в этой зоне нет активных рейсов).")
    else:
        db.insert_airplanes(planes)
        print(f"✅ Загружено самолётов: {len(planes)}")

    # 4. Демонстрация аналитики — подтверждение критериев
    print("\n--- Отчёты (для проверки критериев) ---")

    countries_counts = db.get_countries_and_aeroplanes_count()
    print("Страны и количество самолётов (JOIN):")
    for name, count in countries_counts:
        print(f"  {name}: {count}")

    avg_speed = db.get_avg_speed()
    if avg_speed is not None:
        print(f"Средняя скорость (AVG): {avg_speed:.2f} м/с")
    else:
        print("Средняя скорость: нет данных")

    faster = db.get_aeroplanes_with_higher_speed()
    print(f"Самолётов быстрее средней: {len(faster)}")

    keyword_results = db.get_aeroplanes_with_keyword("ACA")
    print(f"Самолёты с позывным, содержащим 'ACA': {len(keyword_results)}")
    if keyword_results:
        print("Примеры (первые 5):")
        for p in keyword_results[:5]:
            print(f"  ICAO24: {p['icao24']}, callsign: {p['callsign']}")

    db.close()
    print("\n✅ Готово.")


if __name__ == "__main__":
    main()

