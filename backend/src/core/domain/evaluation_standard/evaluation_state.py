from enum import StrEnum
from .standard_verdict import StandardVerdict
from typing import Union


class EvaluationState(StrEnum):
        PASS = "pass"
        FAIL = "fail"
        NA = "not_applicable"
        PENDING = "pending"

        @classmethod
        def from_verdict(cls, verdict: StandardVerdict) -> "EvaluationState":
                """Converte in modo sicuro un verdetto nello stato corrispondente."""
                return cls(verdict)