import os
import pytest
from dotenv import load_dotenv
from aviation.db_manager import DBManager

# Загружаем тестовые переменные окружения
load_dotenv(".env.test")

@pytest.fixture
def db():
    db_mgr = DBManager()
    # Перед каждым тестом очищаем таблицы
    with db_mgr.conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE airplanes, countries RESTART IDENTITY CASCADE;")
    db_mgr.conn.commit()
    yield db_mgr
    db_mgr.close()