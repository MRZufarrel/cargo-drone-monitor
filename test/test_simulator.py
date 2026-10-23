from db import initialize
from repository import get_telemetry_df
from simulator import generate_packet, run


def test_generate_packet_within_bounds(temp_db):
    initialize(temp_db)
    from repository import create_mission
    from datetime import datetime, timezone
    mid = create_mission("M", datetime.now(timezone.utc))
    p = generate_packet(mid)
    assert 3.5 <= p.battery_v <= 4.2
    assert -90.0 <= p.gps_lat <= 90.0
    assert -180.0 <= p.gps_lon <= 180.0
    assert p.mission_status in ("Aktif", "Idle", "Selesai")


def test_run_batch_inserts_rows(temp_db):
    mid = run(samples=10, batch=True)
    df = get_telemetry_df([mid])
    assert len(df) == 10