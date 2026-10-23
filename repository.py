import logging
import sqlite3
from datetime import datetime
from typing import Iterable

import pandas as pd

from db import connection
from models import Mission, TelemetryPacket

logger = logging.getLogger(__name__)


def create_mission(name: str, started_at: datetime) -> int:
    if not name.strip():
        raise ValueError("Mission name must not be empty.")

    sql = "INSERT INTO missions (name, started_at) VALUES (?, ?);"
    with connection() as conn:
        cur = conn.execute(sql, (name.strip(), started_at.isoformat()))
        return cur.lastrowid


def insert_telemetry(packet: TelemetryPacket) -> int:
    sql = """
    INSERT INTO telemetry
        (mission_id, timestamp, gps_lat, gps_lon, battery_v, mission_status, link_up)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    with connection() as conn:
        cur = conn.execute(sql, (
            packet.mission_id,
            packet.timestamp.isoformat(),
            packet.gps_lat,
            packet.gps_lon,
            packet.battery_v,
            packet.mission_status,
            int(packet.link_up),
        ))
        return cur.lastrowid


def insert_many(packets: Iterable[TelemetryPacket]) -> int:
    """Insert batch dalam satu transaksi. Mengembalikan jumlah baris tersimpan."""
    rows = [
        (
            p.mission_id,
            p.timestamp.isoformat(),
            p.gps_lat,
            p.gps_lon,
            p.battery_v,
            p.mission_status,
            int(p.link_up),
        )
        for p in packets
    ]
    if not rows:
        return 0

    sql = """
    INSERT INTO telemetry
        (mission_id, timestamp, gps_lat, gps_lon, battery_v, mission_status, link_up)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    with connection() as conn:
        conn.execute("BEGIN;")
        try:
            conn.executemany(sql, rows)
            conn.execute("COMMIT;")
        except sqlite3.Error:
            conn.execute("ROLLBACK;")
            raise
    return len(rows)


def get_missions() -> list[Mission]:
    sql = "SELECT id, name, started_at FROM missions ORDER BY started_at DESC;"
    with connection() as conn:
        rows = conn.execute(sql).fetchall()
    return [
        Mission(id=r["id"], name=r["name"], started_at=datetime.fromisoformat(r["started_at"]))
        for r in rows
    ]


def get_telemetry_df(mission_ids: list[int] | None = None) -> pd.DataFrame:
    base = """
    SELECT t.id, t.mission_id, m.name AS mission_name, t.timestamp,
           t.gps_lat, t.gps_lon, t.battery_v, t.mission_status, t.link_up
    FROM telemetry t
    JOIN missions m ON m.id = t.mission_id
    """
    params: tuple = ()
    if mission_ids:
        placeholders = ",".join("?" for _ in mission_ids)
        base += f" WHERE t.mission_id IN ({placeholders})"
        params = tuple(mission_ids)
    base += " ORDER BY t.timestamp ASC;"

    with connection() as conn:
        df = pd.read_sql_query(base, conn, params=params)

    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
        df["link_up"] = df["link_up"].astype(bool)
    return df