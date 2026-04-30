# asset.py
from dataclasses import dataclass, field
from .answer import Answer
from .asset_type import AssetType
from .exceptions import RequirementNotFoundError, RequirementAlreadyExistsError
import copy
from types import MappingProxyType

@dataclass
class Asset:
    id: str
    name: str
    asset_type: AssetType
    description: str
    _answers: dict[str, Answer] = field(default_factory=dict, repr=False)

    @classmethod
    def create(cls, asset_id: str, name: str, 
               asset_type: AssetType, description: str,
               answers: list[Answer] | None = None) -> "Asset":
        obj = cls(asset_id, name, asset_type, description)
        for answer in (answers or []):
            obj.add_answer(answer)
        return obj

    # --- lettura ---
    @property
    def answers(self) -> MappingProxyType[str, Answer]:
        return MappingProxyType(self._answers)

    def get_answer(self, requirement_id: str) -> Answer:
        if requirement_id not in self._answers:
            raise RequirementNotFoundError(
                f"Requirement '{requirement_id}' non trovato")
        return self._answers[requirement_id]

    # --- scrittura ---
    def add_answer(self, answer: Answer) -> None:
        if answer.requirement_id in self._answers:
            raise RequirementAlreadyExistsError(
                f"Requisito '{answer.requirement_id}' già presente in '{self.name}'")
        self._answers[answer.requirement_id] = copy.deepcopy(answer)

    def set_node_choice(self, requirement_id: str, 
                        node_id: str, value: bool) -> None:
        self.get_answer(requirement_id).set_node_choice(node_id, value)

    def set_justification(self, requirement_id: str, 
                          justification: str) -> None:
        self.get_answer(requirement_id).set_justification(justification)