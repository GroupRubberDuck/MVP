import uuid
from copy import deepcopy
from ....core.domain.evaluation_object.device import Device
from ....core.ports.outbound.evaluation.get_evaluation_session_port import GetEvaluationSessionPort
from ....core.ports.outbound.evaluation.save_evaluation_session_port import SaveEvaluationSessionPort
from ....core.ports.outbound.evaluation.create_evaluation_session_port import CreateEvaluationSessionPort
from ....core.ports.outbound.evaluation.evaluation_session_exists_port import EvaluationSessionExistsPort
from ....core.ports.outbound.evaluation.close_evaluation_session_port import CloseEvaluationSessionPort
from ....core.domain.session.evaluation_session import EvaluationSession


class InMemoryEvaluationSessionCache(
    GetEvaluationSessionPort,
    SaveEvaluationSessionPort,
    CreateEvaluationSessionPort,
    EvaluationSessionExistsPort,
    CloseEvaluationSessionPort,
):
    def __init__(self):
        self._session: EvaluationSession | None = None

    def create_evaluation_session(
        self,
        standard_id: str,
        device: Device,
    ) -> EvaluationSession:
        if self._session is not None:
            raise RuntimeError("Esiste già una sessione attiva.")
        self._session = deepcopy(EvaluationSession(
            session_id=str(uuid.uuid4()),
            standard_id=standard_id,
            device=device,
        ))
        return deepcopy(self._session)

    def get_evaluation_session(self, session_id: str) -> EvaluationSession:
        if self._session is None:
            raise KeyError("Nessuna sessione attiva.")
        if self._session.session_id != session_id:
            raise KeyError(f"Sessione '{session_id}' non trovata.")
        return deepcopy(self._session)

    def save_evaluation_session(self, session: EvaluationSession) -> None:
        self._session = deepcopy(session)

    def has_active_session(self) -> bool:
        return self._session is not None

    def close_evaluation_session(self, session_id: str) -> None:
        if self._session is None:
            raise KeyError("Nessuna sessione attiva.")
        if self._session.session_id != session_id:
            raise KeyError(f"Sessione '{session_id}' non trovata.")
        self._session = None