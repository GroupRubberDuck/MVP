from .answer import Answer, SnapshotAnswer
from .asset_type import AssetType
from .exceptions import RequirementNotFoundError,RequirementAlreadyExistsError
from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True)
class AssetSnapshot:
        id: str
        name: str
        asset_type: AssetType
        description: str
        answers: MappingProxyType[str, SnapshotAnswer]  

@dataclass(frozen=True)
class AssetSummarySnapshot:
        id: str
        name: str
        asset_type: AssetType
        description: str
        answers:tuple[str, ...]

class Asset:
        def __init__(self, asset_id: str,
                     name: str, 
                     asset_type: AssetType,
                     description: str,
                     answers: dict[str, Answer] | None = None):
            self._id = asset_id
            self._name = name
            self._asset_type = asset_type
            self._description = description
            self._answers: dict[str, Answer] = answers.copy() if answers is not None else {}
        

        @property
        def id(self) -> str:
            return self._id
        
        @property
        def name(self) -> str:
            return self._name
        
        @property
        def asset_type(self) -> AssetType:
            return self._asset_type
        
        @property
        def description(self) -> str:
            return self._description



        def set_name(self, name: str):
            self._name = name


        def set_description(self, description: str):
            self._description = description


        def set_asset_type(self, asset_type: AssetType):
            self._asset_type = asset_type


        def _get_answer(self, requirement_id: str)->Answer:
            if requirement_id not in self._answers:
                raise RequirementNotFoundError(f"Requirement '{requirement_id}' non trovato")
            return self._answers[requirement_id]


        def set_node_choice(self, requirement_id: str, node_id: str, value: bool):
            self._get_answer(requirement_id).set_node_choice(node_id, value)


        def add_answer(self, answer: Answer):
                """Aggiunge una nuova Answer all'Asset."""
                if answer.requirement_id in self._answers:
                    raise RequirementAlreadyExistsError(
                        f"Impossibile aggiungere: il requisito '{answer.requirement_id}' esiste già nell'Asset '{self._name}'."
                    )
                self._answers[answer.requirement_id] = answer

        def set_justification(self, requirement_id: str, justification: str):
            self._get_answer(requirement_id).set_justification(justification)


        def create_snapshot(self) -> AssetSnapshot:
            return AssetSnapshot(
                id=self._id,
                name=self._name,
                asset_type=self._asset_type,
                description=self._description,
                answers=MappingProxyType({req_id: ans.create_snapshot() for req_id, ans in self._answers.items()})
            )
        
        def create_summary_snapshot(self) -> AssetSummarySnapshot:
            return AssetSummarySnapshot(
                id=self._id,
                name=self._name,
                asset_type=self._asset_type,
                description=self._description,
                answers=tuple(self._answers.keys())
            )