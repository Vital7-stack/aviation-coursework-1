import os
from pathlib import Path
import pytest
import psycopg2
from dotenv import load_dotenv

# Загружаем .env ПЕРЕД любыми обращениями к os.environ
load_dotenv()

@pytest.fixture(scope="session")
def db():
    """Фикстура для подключения к БД для тестов."""
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "aviation_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),  # <-- теперь пароль не захардкожен!
    )
    yield conn
    conn.close()


def test_db_connection(db):
    """Проверяет, что соединение с БД устанавливается."""
    with db.cursor() as cur:
        cur.execute("SELECT version();")
        result = cur.fetchone()
    assert result is not None
    print("✅ БД доступна, версия:", result[0])


def test_tables_exist(db):
    """Проверяет наличие таблиц countries и airplanes."""
    with db.cursor() as cur:
        # Проверяем существование таблицы countries
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'countries'
            );
        """)
        assert cur.fetchone()[0] is True

        # Проверяем существование таблицы airplanes
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'airplanes'
            );
        """)
        assert cur.fetchone()[0] is True
    print("✅ Таблицы countries и airplanes существуют.")