from core.ports.inbound.evaluation.evaluation_session.commit_evaluation_session_use_case import (
    CommitEvaluationSessionUseCase,
    CommitEvaluationSessionCommand,
)
from core.ports.inbound.evaluation.exceptions import CommitSessionFailure
from core.ports.outbound.evaluation.get_evaluation_session_port import GetEvaluationSessionPort
from core.ports.outbound.device.repository.save_device_port import SaveDevicePort
from core.ports.outbound.evaluation.exceptions import EvaluationSessionNotFoundError
from core.ports.outbound.device.exceptions import DeviceSaveError

class CommitEvaluationSessionService(CommitEvaluationSessionUseCase):
    def __init__(
        self,
        get_evaluation_session_port: GetEvaluationSessionPort,
        save_device_port: SaveDevicePort,
    ) -> None:
        self._get_session = get_evaluation_session_port
        self._save_device = save_device_port

    def commit(self, command: CommitEvaluationSessionCommand) -> None:
        try:
            session = self._get_session.get_evaluation_session(command.session_id)
        except EvaluationSessionNotFoundError as e:
            raise CommitSessionFailure(
                f"Impossibile fare il commit: Sessione '{command.session_id}' non trovata."
            ) from e

        try:
            self._save_device.save_device(session.device)
        except DeviceSaveError as e: 
            raise CommitSessionFailure(
                f"Errore critico durante il salvataggio del device nel database: {str(e)}"
            ) from e