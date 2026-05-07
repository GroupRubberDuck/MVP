from abc import ABC, abstractmethod
from ....domain.session.evaluation_session import EvaluationSession
from ....domain.evaluation_object.device import Device


class CreateEvaluationSessionPort(ABC):

    @abstractmethod
    def create_evaluation_session(
        self,
        standard_id: str,
        device: Device,
    ) -> EvaluationSession: ...