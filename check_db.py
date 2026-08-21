import psycopg2
from src.aviation.config import DB_CONFIG

def main():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT current_database(), current_user;")
        db_name, user = cur.fetchone()
        print(f"✅ База: {db_name}")
        print(f"✅ Пользователь: {user}")

        # Проверим, что таблицы уже можно создать (если их нет)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS countries (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION
            );
        """)
        print("✅ Таблицы созданы/существуют.")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

if __name__ == "__main__":
    main()