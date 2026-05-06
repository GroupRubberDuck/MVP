from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.domain.evaluation_engine.evaluation_detail import AssetEvaluationDetail


@dataclass(frozen=True)
class GetAssetDetailCommand:
    asset_id: str
    session_id: str


class GetAssetDetailUseCase(ABC):
    @abstractmethod
    def get_asset(self, command: GetAssetDetailCommand) -> AssetEvaluationDetail: ...