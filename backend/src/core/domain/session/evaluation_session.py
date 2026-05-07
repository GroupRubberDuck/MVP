from dataclasses import dataclass
from ..evaluation_object.device import Device

@dataclass
class EvaluationSession:
    session_id: str
    standard_id: str
    device: Device
    