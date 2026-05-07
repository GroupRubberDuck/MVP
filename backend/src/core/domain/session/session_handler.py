from dataclasses import dataclass

@dataclass
class SessionHandler:
    def can_open_session(
        self, active_session_exists: bool
    ) -> bool:
        if active_session_exists:
            return False
        return True
