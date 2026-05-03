# asset.py
from dataclasses import dataclass, field
from .answer import Answer
from .asset_type import AssetType
from .exceptions import AnswerNotFoundError, RequirementAlreadyExistsError
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

    def get_answer(self, requirement_id: str) -> Answer|None:
        if requirement_id not in self._answers:
            return None
        return self._answers[requirement_id]

    # --- scrittura ---
    def add_answer(self, answer: Answer) -> None:
        if answer.requirement_id in self._answers:
            raise RequirementAlreadyExistsError(
                f"Requisito '{answer.requirement_id}' già presente in '{self.name}'")
        self._answers[answer.requirement_id] = answer

    def set_node_choice(self, requirement_id: str, 
                        node_id: str, value: bool) -> None:
        ans=self.get_answer(requirement_id)
        
        if ans is None:
            raise AnswerNotFoundError(
                f"Non esiste una risposta per il requisito '{requirement_id}' in '{self.name}'")
        self._answers[requirement_id] = ans.with_node_choice(node_id, value)

    def set_justification(self, requirement_id: str, 
                          justification: str) -> None:
        ans=self.get_answer(requirement_id)
        if ans is None:
            raise AnswerNotFoundError(
                f"Non esiste una risposta per il requisito '{requirement_id}' in '{self.name}'")
        self._answers[requirement_id] = ans.with_justification(justification)


    def update_info(self, name: str | None = None,
                     asset_type: AssetType | None = None,
                     description: str | None = None) -> None:
        if name is not None:
            self.name = name

        if asset_type is not None: 
            self.asset_type = asset_type

        if description is not None: 
            self.description = description