# compliance_standard.py
from types import MappingProxyType

from .requirement import Requirement
from .evaluation_state import EvaluationState
from .exceptions import RequirementNotFoundError


class ComplianceStandard:
    """
    Non usa frozen=True per lo stesso motivo di DecisionTree:
    costruisce _requirements iterando in __init__ con validazione duplicati.
    Rimane immutabile per costruzione: nessun setter esposto.
    """

    def __init__(self, standard_id: str, name: str, version_number: str,
                 requirements: list[Requirement] | tuple[Requirement, ...]):
        if not standard_id:
            raise ValueError("standard_id non può essere vuoto.")
        if not name:
            raise ValueError("name non può essere vuoto.")

        requirements_dict: dict[str, Requirement] = {}
        for req in requirements:
            if req.requirement_id in requirements_dict:
                raise ValueError(
                    f"Requisito duplicato: '{req.requirement_id}' già presente nello standard.")
            requirements_dict[req.requirement_id] = req

        self._id = standard_id
        self._name = name
        self._version_number = version_number
        self._requirements = requirements_dict

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def version_number(self) -> str:
        return self._version_number

    @property
    def requirements(self) -> tuple[Requirement, ...]:
        return tuple(self._requirements.values())

    def get_requirement(self, requirement_id: str) -> Requirement:
        if requirement_id not in self._requirements:
            raise RequirementNotFoundError(
                f"Requirement '{requirement_id}' non trovato nello standard '{self._name}'.")
        return self._requirements[requirement_id]

    def evaluate_requirement(self, requirement_id: str,
                             answers: MappingProxyType[str, bool]) -> EvaluationState:
        return self.get_requirement(requirement_id).evaluate(answers)