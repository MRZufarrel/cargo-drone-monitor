from datetime import datetime, timezone

import pytest

from db import initialize
from models import TelemetryPacket
from repository import (
    create_mission,
    get_missions,
    get_telemetry_df,
    insert_many,
    insert_telemetry,
)


@pytest.fixture(autouse=True)
def _init(temp_db):
    initialize(temp_db)
    yield


def _sample(mission_id: int) -> TelemetryPacket:
    return TelemetryPacket(
        mission_id=mission_id,
        timestamp=datetime.now(timezone.utc),
        gps_lat=-6.9,
        gps_lon=107.6,
        battery_v=3.9,
        mission_status="Aktif",
        link_up=True,
    )


def test_create_mission_rejects_empty_name():
    with pytest.raises(ValueError):
        create_mission("   ", datetime.now(timezone.utc))


def test_create_and_list_mission():
    mid = create_mission("M1", datetime.now(timezone.utc))
    missions = get_missions()
    assert [m.id for m in missions] == [mid]


def test_insert_telemetry_valid():
    mid = create_mission("M1", datetime.now(timezone.utc))
    row_id = insert_telemetry(_sample(mid))
    assert row_id > 0


def test_battery_check_constraint():
    mid = create_mission("M1", datetime.now(timezone.utc))
    bad = TelemetryPacket(
        mission_id=mid,
        timestamp=datetime.now(timezone.utc),
        gps_lat=-6.9,
        gps_lon=107.6,
        battery_v=9.9,  # di luar CHECK
        mission_status="Aktif",
        link_up=True,
    )
    with pytest.raises(Exception):
        insert_telemetry(bad)


def test_status_check_constraint():
    mid = create_mission("M1", datetime.now(timezone.utc))
    bad = TelemetryPacket(
        mission_id=mid,
        timestamp=datetime.now(timezone.utc),
        gps_lat=-6.9,
        gps_lon=107.6,
        battery_v=3.9,
        mission_status="Terbang",  # bukan enum
        link_up=True,
    )
    with pytest.raises(Exception):
        insert_telemetry(bad)


def test_foreign_key_enforced():
    bad = TelemetryPacket(
        mission_id=9999,
        timestamp=datetime.now(timezone.utc),
        gps_lat=-6.9,
        gps_lon=107.6,
        battery_v=3.9,
        mission_status="Aktif",
        link_up=True,
    )
    with pytest.raises(Exception):
        insert_telemetry(bad)


def test_insert_many_and_read_back():
    mid = create_mission("M1", datetime.now(timezone.utc))
    packets = [_sample(mid) for _ in range(5)]
    assert insert_many(packets) == 5
    df = get_telemetry_df([mid])
    assert len(df) == 5
    assert df["link_up"].all()