from dataclasses import dataclass
from .session_type import SessionType


@dataclass
class Session:
    session_id: str
    standard_id: str
    device_id: str
    session_type: SessionType