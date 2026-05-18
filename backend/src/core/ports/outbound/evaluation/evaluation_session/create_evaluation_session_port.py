from abc import ABC, abstractmethod
from core.domain.session.evaluation_session import EvaluationSession
from core.domain.evaluation_object.device import Device
from core.domain.evaluation_standard.compliance_standard import ComplianceStandard


class CreateEvaluationSessionPort(ABC):
    @abstractmethod
    def create_evaluation_session(
        self,
        standard: ComplianceStandard,
        device: Device,
    ) -> EvaluationSession: ...
