from core.domain.evaluation_engine.evaluation_detail import AssetEvaluationDetail
from core.ports.inbound.asset.exceptions import GetAssetDetailFailure
from core.ports.inbound.asset.get_asset_detail_use_case import (
    GetAssetDetailCommand,
    GetAssetDetailUseCase,
)
from core.ports.outbound.evaluation.exceptions import AssetNotInSessionError, SessionNotFoundError
from core.ports.outbound.evaluation.get_session_port import GetSessionPort


class GetAssetDetailService(GetAssetDetailUseCase):
    def __init__(self, get_session_port: GetSessionPort) -> None:
        self._get_session_port = get_session_port

    def get_asset(self, command: GetAssetDetailCommand) -> AssetEvaluationDetail:
        try:
            session = self._get_session_port.get_session(command.session_id)
        except SessionNotFoundError:
            raise GetAssetDetailFailure(
                f"Sessione '{command.session_id}' non trovata."
            )

        try:
            return session.get_asset_detail(command.asset_id)
        except AssetNotInSessionError:
            raise GetAssetDetailFailure(
                f"Asset '{command.asset_id}' non presente nella sessione."
            )