from core.ports.inbound.evaluation.evaluation_session.close_evaluation_session_use_case import (
    CloseEvaluationSessionUseCase,
    CloseEvaluationSessionCommand,
)
from core.ports.outbound.evaluation.evaluation_session.close_evaluation_session_port import (
    CloseEvaluationSessionPort,
)


class CloseEvaluationSessionService(CloseEvaluationSessionUseCase):
    def __init__(self, delete_session_port: CloseEvaluationSessionPort) -> None:
        self._delete_session = delete_session_port

    def close_evaluation_session(self, command: CloseEvaluationSessionCommand) -> None:
        self._delete_session.close_evaluation_session(command.session_id)
