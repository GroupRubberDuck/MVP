from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.domain.evaluation_object.asset.asset_type import AssetType


@dataclass(frozen=True)
class UpdateAssetCommand:
    asset_id: str
    name: str
    type: AssetType
    description: str
    session_id: str


class UpdateAssetUseCase(ABC):
    @abstractmethod
    def update_asset(self, update_command: UpdateAssetCommand) -> None: ...