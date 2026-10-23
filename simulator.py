import logging
import random
import time
from datetime import datetime, timezone

from config import (
    BATTERY_MAX_V,
    BATTERY_MIN_V,
    GPS_BOUNDS,
    LINK_LOSS_PROBABILITY,
    MISSION_STATUSES,
)
from db import initialize
from models import TelemetryPacket
from repository import create_mission, insert_many, get_telemetry_df

logger = logging.getLogger(__name__)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def generate_packet(mission_id: int) -> TelemetryPacket:
    return TelemetryPacket(
        mission_id=mission_id,
        timestamp=_now_utc(),
        gps_lat=round(random.uniform(GPS_BOUNDS["lat_min"], GPS_BOUNDS["lat_max"]), 6),
        gps_lon=round(random.uniform(GPS_BOUNDS["lon_min"], GPS_BOUNDS["lon_max"]), 6),
        battery_v=round(random.uniform(BATTERY_MIN_V, BATTERY_MAX_V), 3),
        mission_status=random.choice(MISSION_STATUSES),
        link_up=random.random() > LINK_LOSS_PROBABILITY,
    )


def run(samples: int = 20, interval_s: float = 0.5, batch: bool = True) -> int:
    """Menjalankan simulasi. Jika batch=True, semua sampel disimpan sekaligus."""
    initialize()
    mission_id = create_mission(
        name=f"Sim {_now_utc().strftime('%Y%m%d-%H%M%S')}",
        started_at=_now_utc(),
    )
    logger.info("Created mission id=%s", mission_id)

    if batch:
        packets = [generate_packet(mission_id) for _ in range(samples)]
        inserted = insert_many(packets)
        logger.info("Inserted %s telemetry packets", inserted)
        return mission_id

    for i in range(samples):
        packet = generate_packet(mission_id)
        insert_many([packet])
        logger.info(
            "[%d/%d] t=%s bat=%.3fV status=%s link=%s",
            i + 1, samples,
            packet.timestamp.isoformat(timespec="seconds"),
            packet.battery_v,
            packet.mission_status,
            "UP" if packet.link_up else "DOWN",
        )
        if i < samples - 1:
            time.sleep(interval_s)
    return mission_id


def _print_recent(mission_id: int, limit: int = 10) -> None:
    df = get_telemetry_df([mission_id]).tail(limit)
    if df.empty:
        print("(no telemetry)")
        return
    print(df.to_string(index=False))


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    mid = run(samples=20, interval_s=0.3, batch=False)
    print()
    _print_recent(mid, limit=20)