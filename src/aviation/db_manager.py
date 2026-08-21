import psycopg2
from psycopg2.extras import execute_values
from typing import List
from .config import DB_CONFIG
from .models import Country, Airplane

class DBManager:
    def __init__(self):
        self.conn = psycopg2.connect(**DB_CONFIG)

    def ensure_tables_exist(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS countries (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    latitude DOUBLE PRECISION,
                    longitude DOUBLE PRECISION
                );

                CREATE TABLE IF NOT EXISTS airplanes (
                    icao24 VARCHAR(10) PRIMARY KEY,
                    callsign VARCHAR(20),
                    origin_country VARCHAR(255),
                    time_position DOUBLE PRECISION,
                    last_seen DOUBLE PRECISION,
                    longitude DOUBLE PRECISION,
                    latitude DOUBLE PRECISION,
                    baro_altitude DOUBLE PRECISION,
                    on_ground BOOLEAN,
                    velocity DOUBLE PRECISION,
                    true_track DOUBLE PRECISION,
                    vertical_rate DOUBLE PRECISION,
                    squawk VARCHAR(4),
                    spi BOOLEAN,
                    geo_altitude DOUBLE PRECISION
                );
            """)
        self.conn.commit()

    def insert_countries(self, countries: List[Country]):
        values = [
            (c.name, c.latitude, c.longitude)
            for c in countries
        ]
        with self.conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO countries (name, latitude, longitude)
                VALUES %s
                ON CONFLICT (name) DO NOTHING;
                """,
                values,
            )
        self.conn.commit()

    def insert_airplanes(self, airplanes: List[Airplane]):
        values = [
            (
                a.icao24, a.callsign, a.origin_country, a.time_position,
                a.last_seen, a.longitude, a.latitude, a.baro_altitude,
                a.on_ground, a.velocity, a.true_track, a.vertical_rate,
                a.squawk, a.spi, a.geo_altitude
            )
            for a in airplanes
        ]
        with self.conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO airplanes (
                    icao24, callsign, origin_country, time_position, last_seen,
                    longitude, latitude, baro_altitude, on_ground, velocity,
                    true_track, vertical_rate, squawk, spi, geo_altitude
                ) VALUES %s
                ON CONFLICT (icao24) DO UPDATE SET
                    callsign = EXCLUDED.callsign,
                    velocity = EXCLUDED.velocity;
                """,
                values,
            )
        self.conn.commit()

    def get_countries_and_aeroplanes_count(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT c.name, COUNT(a.icao24)
                FROM countries c
                LEFT JOIN airplanes a ON a.origin_country = c.name
                GROUP BY c.id, c.name;
            """)
            return cur.fetchall()

    def get_all_aeroplanes(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM airplanes;")
            cols = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            return [dict(zip(cols, row)) for row in rows]

    def get_avg_speed(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT AVG(velocity) FROM airplanes;")
            r = cur.fetchone()[0]
            return float(r) if r is not None else None

    def get_aeroplanes_with_higher_speed(self):
        avg = self.get_avg_speed()
        if avg is None:
            return []
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM airplanes WHERE velocity > %s;", (avg,))
            cols = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            return [dict(zip(cols, row)) for row in rows]

    def get_aeroplanes_with_keyword(self, keyword: str):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM airplanes WHERE callsign ILIKE %s;",
                (f"%{keyword}%",)
            )
            cols = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            return [dict(zip(cols, row)) for row in rows]

    def close(self):
        if self.conn:
            self.conn.close()