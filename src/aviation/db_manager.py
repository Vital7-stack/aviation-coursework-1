import psycopg2
from psycopg2.extras import execute_values
from typing import List, Tuple, Optional, Dict, Any
from .config import DB_CONFIG
from .models import Country, Airplane


class DBManager:
    """
    Класс для работы с БД PostgreSQL.
    Отвечает за подключение, CRUD, аналитические запросы.
    Реализует требуемые методы для курсовой работы.
    """

    def __init__(self):
        # Подключение к БД
        self.conn = psycopg2.connect(**DB_CONFIG)
        # Отключаем автокоммит, чтобы явно контролировать транзакции
        self.conn.autocommit = False

    def close(self):
        """Закрывает соединение с БД, если оно открыто."""
        if self.conn and not self.conn.closed:
            self.conn.close()

    # --- CRUD ---
    def insert_countries(self, countries: List[Country]) -> None:
        sql = """
            INSERT INTO countries (name, latitude, longitude)
            VALUES %s
            ON CONFLICT (name) DO NOTHING;
        """
        values = [
            (c.name, c.latitude, c.longitude)
            for c in countries
        ]
        # Создаём курсор локально — так надёжнее и чище
        with self.conn.cursor() as cur:
            execute_values(cur, sql, values)
        self.conn.commit()

    def insert_airplanes(self, airplanes: List[Airplane]) -> None:
        sql = """
            INSERT INTO airplanes (
                icao24, callsign, origin_country, velocity, latitude, longitude
            ) VALUES %s
            ON CONFLICT (icao24) DO UPDATE SET
                callsign = EXCLUDED.callsign,
                origin_country = EXCLUDED.origin_country,
                velocity = EXCLUDED.velocity,
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude;
        """
        values = [
            (
                a.icao24,
                a.callsign,
                a.origin_country,
                a.velocity,
                a.latitude,
                a.longitude,
            )
            for a in airplanes
        ]
        with self.conn.cursor() as cur:
            execute_values(cur, sql, values)
        self.conn.commit()

    def get_countries_and_aeroplanes_count(self) -> List[Tuple[str, int]]:
        """
        Получает список всех стран и количество самолётов в их воздушных пространствах.
        Использует JOIN по названию страны (origin_country), так как в текущей схеме
        нет country_id в airplanes.
        Возвращает список кортежей (country_name, count).
        """
        sql = """
            SELECT c.name, COUNT(a.icao24) AS airplane_count
            FROM countries c
            LEFT JOIN airplanes a ON c.name = a.origin_country
            GROUP BY c.id, c.name
            ORDER BY airplane_count DESC;
        """
        with self.conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()

    def get_all_aeroplanes(self) -> List[Dict[str, Any]]:
        """
        Получает все записи из таблицы airplanes.
        Возвращает список словарей, где ключи — имена колонок.
        """
        sql = "SELECT * FROM airplanes;"
        with self.conn.cursor() as cur:
            cur.execute(sql)
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            return [dict(zip(columns, row)) for row in rows]

    def get_avg_speed(self) -> Optional[float]:
        """
        Вычисляет среднюю скорость по всем самолётам (поле velocity).
        Возвращает float или None, если нет данных.
        """
        sql = "SELECT AVG(velocity) FROM airplanes WHERE velocity IS NOT NULL;"
        with self.conn.cursor() as cur:
            cur.execute(sql)
            result = cur.fetchone()[0]
            return float(result) if result is not None else None

    def get_aeroplanes_with_higher_speed(self) -> List[Dict[str, Any]]:
        """
        Получает список самолётов, у которых скорость выше средней.
        Расчёт средней скорости и фильтрация выполняются в одном запросе (CTE).
        """
        sql = """
            WITH stats AS (
                SELECT AVG(velocity) AS avg_velocity
                FROM airplanes
                WHERE velocity IS NOT NULL
            )
            SELECT a.*
            FROM airplanes a
            CROSS JOIN stats s
            WHERE a.velocity > s.avg_velocity AND a.velocity IS NOT NULL;
        """
        with self.conn.cursor() as cur:
            cur.execute(sql)
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            return [dict(zip(columns, row)) for row in rows]

    def get_aeroplanes_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Ищет самолёты, в позывном (callsign) которых содержится заданная подстрока.
        Поиск регистронезависимый (ILIKE).
        Пример: 'ACA' найдёт самолёты Air Canada.
        """
        pattern = f"%{keyword}%"
        sql = """
            SELECT *
            FROM airplanes
            WHERE callsign ILIKE %s;
        """
        with self.conn.cursor() as cur:
            cur.execute(sql, (pattern,))
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            return [dict(zip(columns, row)) for row in rows]