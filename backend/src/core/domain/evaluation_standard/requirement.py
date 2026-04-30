from .decision_tree import DecisionTree
from types import MappingProxyType
from .evaluation_state import EvaluationState
class Requirement:
    def __init__(self, id: str,name:str, 
                 description: str, target_description: str, 
                 dependency_ids: list[str] | tuple[str, ...] | None = None,
                 decision_tree: DecisionTree | None = None):
    
        self._id = id
        self._name = name
        self._description = description
        self._target_description = target_description
        self._dependency_ids = tuple(dependency_ids) if dependency_ids is not None else ()
        self._decision_tree = decision_tree

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def decision_tree(self) -> DecisionTree | None:
        return self._decision_tree
    
    @property
    def target_description(self) -> str:
        return self._target_description

    @property
    def dependency_ids(self) -> tuple[str, ...]:
        return self._dependency_ids
    
    def evaluate(self, answers: MappingProxyType[str, bool]) -> EvaluationState:
        if self._decision_tree is None:
            raise ValueError(f"Il requirement '{self._id}' non ha un albero decisionale associato.")
        return self._decision_tree.evaluate(answers)