from types import MappingProxyType
from .requirement import Requirement
from .evaluation_state import EvaluationState

class ComplianceStandard:
    def __init__(self, standard_id: str, name: str, version_number: str, 
                 requirements: list[Requirement] | tuple[Requirement, ...]):
        self._id = standard_id
        self._name = name
        self._version_number = version_number
        
        self._requirements: dict[str, Requirement] = {}
        # Controllo duplicati in ingresso (come per l'albero decisionale)
        for req in requirements:
            if req.id in self._requirements:
                raise ValueError(f"Requisito duplicato: L'id '{req.id}' è già presente nello standard.")
            self._requirements[req.id] = req

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
        """Restituisce i requisiti in una tupla protetta da modifiche strutturali."""
        return tuple(self._requirements.values())

    def get_requirement(self, requirement_id: str) -> Requirement:
        """Metodo di utility per estrarre un singolo requisito (utile per l'Application Service)"""
        if requirement_id not in self._requirements:
            raise ValueError(f"Requirement con id '{requirement_id}' non trovato nello standard '{self._name}'.")
        return self._requirements[requirement_id]

    def evaluate_requirement(self, requirement_id: str, answers: MappingProxyType[str, bool]) -> EvaluationState:
        # Riutilizza il metodo get_requirement per non duplicare la logica dell'eccezione
        req = self.get_requirement(requirement_id)
        return req.evaluate(answers)