import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from config import DB_BUSY_TIMEOUT_MS, get_db_path

logger = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS missions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,
    started_at      TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS telemetry (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id      INTEGER NOT NULL,
    timestamp       TEXT    NOT NULL,
    gps_lat         REAL    NOT NULL CHECK (gps_lat BETWEEN -90.0 AND 90.0),
    gps_lon         REAL    NOT NULL CHECK (gps_lon BETWEEN -180.0 AND 180.0),
    battery_v       REAL    NOT NULL CHECK (battery_v BETWEEN 3.0 AND 4.3),
    mission_status  TEXT    NOT NULL CHECK (mission_status IN ('Aktif', 'Idle', 'Selesai')),
    link_up         INTEGER NOT NULL CHECK (link_up IN (0, 1)),
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_telemetry_mission_time
    ON telemetry (mission_id, timestamp);
"""


@contextmanager
def connection(db_path: Path | None = None) -> Iterator[sqlite3.Connection]:
    """Context manager yang benar-benar menutup koneksi SQLite.

    Jika db_path None, path dibaca dari environment SAAT FUNGSI DIPANGGIL,
    bukan saat modul di-import. Ini penting supaya test bisa mengganti
    CARGO_DRONE_DB lewat monkeypatch tanpa reload modul.
    """
    path = db_path if db_path is not None else get_db_path()
    conn = sqlite3.connect(
        path,
        timeout=DB_BUSY_TIMEOUT_MS / 1000,
        isolation_level=None,  # autocommit; transaksi eksplisit via BEGIN
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute(f"PRAGMA busy_timeout = {DB_BUSY_TIMEOUT_MS};")
    try:
        yield conn
    finally:
        conn.close()


def initialize(db_path: Path | None = None) -> None:
    """Membuat skema jika belum ada. Idempotent."""
    path = db_path if db_path is not None else get_db_path()
    logger.info("Initializing database at %s", path)
    with connection(path) as conn:
        conn.executescript(SCHEMA)