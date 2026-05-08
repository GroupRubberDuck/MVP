from core.domain.evaluation_object.asset.asset_anagraphic import AssetAnagraphic
from core.domain.evaluation_object.exceptions import AssetNotFoundError
from core.ports.inbound.asset.exceptions import GetAssetAnagraphicFailure
from core.ports.inbound.asset.get_asset_anagraphic_use_case import (
    GetAssetAnagraphicCommand,
    GetAssetAnagraphicUseCase,
)
from core.ports.outbound.evaluation.exceptions import SessionNotFoundError
from core.ports.outbound.evaluation.get_session_port import GetSessionPort


class GetAssetAnagraphicService(GetAssetAnagraphicUseCase):
    def __init__(self, get_session_port: GetSessionPort) -> None:
        self._get_session_port = get_session_port

    def get_asset_anagraphic(self, command: GetAssetAnagraphicCommand) -> AssetAnagraphic:
        try:
            session = self._get_session_port.get_session(command.session_id)
        except SessionNotFoundError:
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