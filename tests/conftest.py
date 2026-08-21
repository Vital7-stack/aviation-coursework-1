import pytest
from aviation.db_manager import DBManager

@pytest.fixture
def db():
    mgr = DBManager()
    with mgr.conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE airplanes, countries RESTART IDENTITY CASCADE;")
    mgr.conn.commit()
    yield mgr
    mgr.close()