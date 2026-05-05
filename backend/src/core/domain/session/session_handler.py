from dataclasses import dataclass
from .session_type import SessionType

@dataclass
class SessionHandler:
    def can_open_session(
        self, requested_type: SessionType, active_session_exists: bool
    ) -> bool:
        if active_session_exists:
            return False
        return True
