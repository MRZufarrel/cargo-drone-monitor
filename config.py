import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


def get_db_path() -> Path:
    """Baca DB path dari env setiap kali dipanggil.

    Penting: jangan simpan hasilnya di konstanta modul, karena test
    yang mengganti CARGO_DRONE_DB lewat monkeypatch perlu melihat
    nilai baru tanpa reload modul.
    """
    return Path(os.getenv("CARGO_DRONE_DB", BASE_DIR / "cargo_drone.db"))


# Kompatibilitas untuk kode lama yang masih `from config import DB_PATH`.
# Untuk kode baru, gunakan get_db_path().
DB_PATH = get_db_path()

DB_BUSY_TIMEOUT_MS = int(os.getenv("DB_BUSY_TIMEOUT_MS", "5000"))

GPS_BOUNDS = {
    "lat_min": float(os.getenv("GPS_LAT_MIN", "-6.95")),
    "lat_max": float(os.getenv("GPS_LAT_MAX", "-6.85")),
    "lon_min": float(os.getenv("GPS_LON_MIN", "107.55")),
    "lon_max": float(os.getenv("GPS_LON_MAX", "107.65")),
}

BATTERY_MIN_V = 3.5
BATTERY_MAX_V = 4.2
BATTERY_CRITICAL_V = 3.6

MISSION_STATUSES = ("Aktif", "Idle", "Selesai")
LINK_LOSS_PROBABILITY = 0.15