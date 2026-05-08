from abc import ABC, abstractmethod
from core.domain.evaluation_object.asset.asset_type import AssetType
from pydantic import BaseModel

class CreateAssetCommand(BaseModel):
    device_id: str
    name: str
    asset_type: AssetType
    description: str
    session_id: str

class CreateAssetUseCase(ABC):

    @abstractmethod
    def create_asset(self, command: CreateAssetCommand) -> str: 
        """ritorna l'id dell'asset creato"""
        ...