from dotenv import load_dotenv
import os
import psycopg2

# Загружаем переменные из .env
load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

    with conn.cursor() as cur:
        cur.execute("SELECT current_database(), version();")
        db_name, version = cur.fetchone()
        print(f"✅ Успешное подключение к базе: {db_name}")
        print(f"📦 Версия PostgreSQL: {version}")

        # Проверим, что таблицы действительно создались
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('countries', 'airplanes');
        """)
        tables = cur.fetchall()
        print(f"🗄️ Найдены таблицы: {[t for t in tables]}")

except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
finally:
    if 'conn' in locals() and conn:
        conn.close()