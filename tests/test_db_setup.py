import psycopg2

TEST_DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "aviation_test",
    "user": "postgres",
    "password": "556677"  # <-- Вставь свой пароль, если он другой
}

def get_test_connection():
    return psycopg2.connect(**TEST_DB_CONFIG)

def test_countries_table_exists_and_has_data():
    conn = get_test_connection()
    try:
        with conn.cursor() as cur:
            # 1. Проверка существования таблицы countries
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                      AND table_name = 'countries'
                );
            """)
            # fetchone() вернёт кортеж вида (True,) или (False,) → берём [0]
            table_exists = cur.fetchone()[0]
            assert table_exists is True, "Таблица countries не найдена!"

            # 2. Проверка количества строк в countries
            cur.execute("SELECT COUNT(*) FROM countries;")
            # fetchone() вернёт (3,) → берём [0], будет число 3
            row_count = cur.fetchone()[0]
            assert row_count > 0, f"В таблице countries нет данных. Найдено строк: {row_count}"

            # 3. Проверка существования таблицы airplanes
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                      AND table_name = 'airplanes'
                );
            """)
            planes_table_exists = cur.fetchone()[0]
            assert planes_table_exists is True, "Таблица airplanes не найдена!"

    finally:
        conn.close()