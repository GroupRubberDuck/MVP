from abc import ABC, abstractmethod

@dataclass(frozen=True)
class DeleteAssetCommand:
    asset_id: str

class DeleteAssetUseCase(ABC):
    @abstractmethod
    def delete_asset(delete_command: DeleteAssetCommand) -> None: ...