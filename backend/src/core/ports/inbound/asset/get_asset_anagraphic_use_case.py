from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.domain.evaluation_object.asset.asset_anagraphic import AssetAnagraphic


@dataclass(frozen=True)
class GetAssetAnagraphicCommand:
    device_id: str
    asset_id: str
    session_id: str


class GetAssetAnagraphicUseCase(ABC):
    @abstractmethod
    def get_asset_anagraphic(
        self, command: GetAssetAnagraphicCommand
    ) -> AssetAnagraphic: 
        """Restituisce l'anagrafica dell'asset specificato.

        Raises:
            GetAssetAnagraphicFailure: se la sessione o l'asset non esistono.
        """
        ...