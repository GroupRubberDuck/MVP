
# requirement.py
from dataclasses import dataclass, field
from core.domain.evaluation_object.answer import Answer 
from core.domain.evaluation_object.asset import AssetEvidence
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

    def evaluate(self, answer: AssetEvidence,
                 dependency_states: tuple[tuple[str, EvaluationState], ...] = ()
                 ) -> EvaluationState:
        blocked = self._check_dependencies(dependency_states)
        if blocked is not None:
            return blocked
        if self.decision_tree is None:
            raise MissingDecisionTreeError(
                f"Il requirement '{self.requirement_id}' non ha un albero decisionale associato.")
        state = self.decision_tree.evaluate(answer.node_choices)
        if state == EvaluationState.NA and not answer.justification.strip():
            return EvaluationState.FAIL
        return state
    

    def _check_dependencies(self,
                            dependencies: tuple[tuple[str, EvaluationState], ...]
                            ) -> EvaluationState | None:
        if not dependencies:
            return None
        states = {s for _, s in dependencies}
        if EvaluationState.FAIL in states:
            return EvaluationState.FAIL
        if EvaluationState.PENDING in states:
            return EvaluationState.PENDING
        if EvaluationState.NA in states:
            return EvaluationState.NA
        return None