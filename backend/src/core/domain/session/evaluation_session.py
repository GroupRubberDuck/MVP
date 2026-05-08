from dataclasses import dataclass
from core.domain.evaluation_object.device import Device
from core.domain.evaluation_standard.compliance_standard import ComplianceStandard

@dataclass
class EvaluationSession:
    session_id: str
    standard: ComplianceStandard
    device: Device
