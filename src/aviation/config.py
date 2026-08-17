
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME", "aviation_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}

# Для трекера «прямо сейчас» берём states/all
OPENSKY_URL = "https://opensky-network.org/api/states/all"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

USER_AGENT = "aviation-coursework-py3.14/1.0 (contact: zinabir7@gmail.com)"