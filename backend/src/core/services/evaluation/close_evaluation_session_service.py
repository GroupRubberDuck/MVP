from core.ports.inbound.evaluation.evaluation_session.close_evaluation_session_use_case import CloseEvaluationSessionUseCase
from core.ports.outbound.evaluation.delete_session_port import DeleteSessionPort
from core.services.evaluation.close_evaluation_session_command import CloseEvaluationSessionCommand


class CloseEvaluationSessionService(CloseEvaluationSessionUseCase):

    def __init__(self, delete_session_port: DeleteSessionPort) -> None:
        self._delete_session = delete_session_port

    def close_evaluation_session(self, command: CloseEvaluationSessionCommand) -> None:
        self._delete_session.delete_session(command.session_id)