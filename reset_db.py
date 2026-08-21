import psycopg2
from aviation.config import DB_CONFIG

conn = psycopg2.connect(**DB_CONFIG)
with conn.cursor() as cur:
    # Удаляем таблицы полностью
    cur.execute("DROP TABLE IF EXISTS airplanes;")
    cur.execute("DROP TABLE IF EXISTS countries;")
conn.commit()
conn.close()
print("✅ Таблицы удалены. Теперь запускаем main.py")