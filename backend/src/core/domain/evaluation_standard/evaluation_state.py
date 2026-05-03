from enum import StrEnum
from .standard_verdict import StandardVerdict


class EvaluationState(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    NA = "not_applicable"
    PENDING = "pending"

    @classmethod
    def from_verdict(cls, verdict: StandardVerdict) -> "EvaluationState":
        mapping = {
            StandardVerdict.PASS: cls.PASS,
            StandardVerdict.FAIL: cls.FAIL,
            StandardVerdict.NA: cls.NA,
        }
        result = mapping.get(verdict)
        if result is None:
            raise ValueError(
                f"StandardVerdict '{verdict}' non ha un EvaluationState corrispondente.")
        return result