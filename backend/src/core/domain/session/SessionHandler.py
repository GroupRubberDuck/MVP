from core.domain.session.session_type import SessionType


class SessionHandler:
    def can_open_session(
        self, requested_type: SessionType, active_session_exists: bool
    ) -> bool:
        if active_session_exists:
            return False
        return True
