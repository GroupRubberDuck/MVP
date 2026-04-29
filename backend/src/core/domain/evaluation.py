from pydantic import BaseModel, Enum

from .evaluation_object.device import Device
from .compliance_standard import ComplianceStandard

class EvaluationState(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NA = "NA"
    PENDING = "PENDING"

class EvaluationSheet(BaseModel):
    device: Device
    standard: ComplianceStandard

