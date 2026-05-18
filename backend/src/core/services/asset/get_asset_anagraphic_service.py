from core.domain.evaluation_object.asset.asset_anagraphic import AssetAnagraphic
from core.domain.evaluation_object.exceptions import AssetNotFoundError
from core.ports.inbound.asset.exceptions import GetAssetAnagraphicFailure
from core.ports.inbound.asset.get_asset_anagraphic_use_case import (
    GetAssetAnagraphicCommand,
    GetAssetAnagraphicUseCase,
)
from core.ports.outbound.evaluation.exceptions import EvaluationSessionNotFoundError
from core.ports.outbound.evaluation.get_evaluation_session_port import (
    GetEvaluationSessionPort,
)


class GetAssetAnagraphicService(GetAssetAnagraphicUseCase):
    def __init__(self, get_evaluation_session_port: GetEvaluationSessionPort) -> None:
        self._get_evaluation_session_port = get_evaluation_session_port

    def get_asset_anagraphic(
        self, command: GetAssetAnagraphicCommand
    ) -> AssetAnagraphic:
        try:
            session = self._get_evaluation_session_port.get_evaluation_session(
                command.session_id
            )
        except EvaluationSessionNotFoundError:
            raise GetAssetAnagraphicFailure(
                f"Sessione '{command.session_id}' non trovata."
            )

        try:
            asset = session.device.get_asset(command.asset_id)
        except AssetNotFoundError:
            raise GetAssetAnagraphicFailure(
                f"Asset '{command.asset_id}' non trovato nel dispositivo."
            )

        return asset.anagraphic
