from abc import ABC, abstractmethod
from pydantic import BaseModel


class DeleteAssetCommand(BaseModel):
    device_id: str
    asset_id: str
    session_id: str


class DeleteAssetUseCase(ABC):
    @abstractmethod
    def delete_asset(self, command: DeleteAssetCommand) -> None: ...
