from pydantic import BaseModel
from abc import ABC, abstractmethod

class EvaluateDecisionNodeCommand(BaseModel):
    session_id: str
    device_id: str
    asset_id: str
    requirement_id: str
    node_id: str
    answer: bool

class EvaluateDecisionNodeUseCase(ABC):
    @abstractmethod
    def evaluate_node(self, command: EvaluateDecisionNodeCommand) -> None:
        pass