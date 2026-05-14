from core.ports.inbound.evaluation.get_active_session_use_case import (
    ActiveSessionInfo,
    GetActiveSessionUseCase,
)
from core.ports.outbound.evaluation.get_active_session_port import GetActiveSessionPort


class GetActiveSessionService(GetActiveSessionUseCase):
    def __init__(self, get_active_session_port: GetActiveSessionPort) -> None:
        self._get_active_session_port = get_active_session_port

    def get_active_session(self) -> ActiveSessionInfo | None:
        session = self._get_active_session_port.get_active_session()
        if session is None:
            return None
        return ActiveSessionInfo(
            session_id=session.session_id,
            device_id=session.device.id,
        )