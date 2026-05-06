from dataclasses import dataclass


@dataclass
class EvaluationSession:
    session_id: str
    standard: Standard
    device: Device