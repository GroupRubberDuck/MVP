from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.domain.evaluation_object.asset.asset_type import AssetType


@dataclass(frozen=True)
class UpdateAssetCommand:
    device_id: str
    asset_id: str
    name: str
    asset_type: AssetType
    description: str
    session_id: str


class UpdateAssetUseCase(ABC):
    @abstractmethod
    def update_asset(self, update_command: UpdateAssetCommand) -> None: 
        """Aggiorna l'anagrafica di un asset esistente.

        Raises:
            UpdateAssetFailure: se la sessione o l'asset non esistono, i dati
                non sono validi, o il salvataggio fallisce.
        """
        ... 
