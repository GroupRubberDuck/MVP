from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.domain.evaluation_engine.evaluation_detail import AssetEvaluationDetail


@dataclass(frozen=True)
class GetAssetEvaluationDetailCommand:
    device_id: str
    asset_id: str
    session_id: str


class GetAssetEvaluationDetailUseCase(ABC):
    @abstractmethod
    def get_asset(
        self, command: GetAssetEvaluationDetailCommand
    ) -> AssetEvaluationDetail:
        """Restituisce il dettaglio di valutazione dell'asset specificato.

        Raises:
            GetAssetDetailFailure: se la sessione o l'asset non esistono.
        """
        ...
