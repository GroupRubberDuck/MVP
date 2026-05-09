from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.domain.evaluation_engine.evaluation_detail import RequirementEvaluationDetail


@dataclass(frozen=True)
class GetRequirementEvaluationDetailCommand:
    requirement_id: str
    asset_id: str
    device_id: str
    session_id: str


class GetRequirementEvaluationDetailUseCase(ABC):
    @abstractmethod
    def get_evaluation_detail(
        self, command: GetRequirementEvaluationDetailCommand
    ) -> RequirementEvaluationDetail: ...