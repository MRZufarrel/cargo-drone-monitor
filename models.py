from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Mission:
    id: int
    name: str
    started_at: datetime


@dataclass(frozen=True)
class TelemetryPacket:
    mission_id: int
    timestamp: datetime
    gps_lat: float
    gps_lon: float
    battery_v: float
    mission_status: str
    link_up: bool