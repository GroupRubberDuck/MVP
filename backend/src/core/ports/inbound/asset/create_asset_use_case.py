from abc import ABC, abstractmethod
from ....services.asset.create_asset_command import CreateAssetCommand

class CreateAssetUseCase(ABC):

    @abstractmethod
    def create_asset(self, command: CreateAssetCommand) -> bool: ...