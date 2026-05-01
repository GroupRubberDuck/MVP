
# requirement.py
from dataclasses import dataclass, field
from types import MappingProxyType
 
from .decision_tree import DecisionTree
from .evaluation_state import EvaluationState
from .exceptions import MissingDecisionTreeError
 
 
@dataclass(frozen=True)
class Requirement:
    requirement_id: str
    name: str
    description: str
    target_description: str
    dependency_ids: tuple[str, ...] = field(default_factory=tuple)
    decision_tree: DecisionTree | None = None
 
    def __post_init__(self):
        if not self.requirement_id:
            raise ValueError("requirement_id non può essere vuoto.")
 
    def evaluate(self, answers: MappingProxyType[str, bool]) -> EvaluationState:
        if self.decision_tree is None:
            raise MissingDecisionTreeError(
                f"Il requirement '{self.requirement_id}' non ha un albero decisionale associato.")
        return self.decision_tree.evaluate(answers)
 
