from core.ports.inbound.asset.exceptions import DeleteAssetFailure
from core.ports.inbound.asset.delete_asset_use_case import (
    DeleteAssetCommand,
    DeleteAssetUseCase,
)
from core.ports.outbound.evaluation.get_evaluation_session_port import (
    GetEvaluationSessionPort,
)
from core.ports.outbound.evaluation.evaluation_session.save_evaluation_session_port import (
    SaveEvaluationSessionPort,
)
from core.ports.outbound.evaluation.exceptions import EvaluationSessionNotFoundError
from core.domain.evaluation_object.exceptions import AssetNotFoundError


class DeleteAssetService(DeleteAssetUseCase):
    def __init__(
        self,
        save_evaluation_session_port: SaveEvaluationSessionPort,
        get_evaluation_session_port: GetEvaluationSessionPort,
    ) -> None:
        self._save_evaluation_session_port = save_evaluation_session_port
        self._get_evaluation_session_port = get_evaluation_session_port

    def delete_asset(self, command: DeleteAssetCommand) -> None:
        try:
            session = self._get_evaluation_session_port.get_evaluation_session(
                command.session_id
            )
        except EvaluationSessionNotFoundError as e:
            raise DeleteAssetFailure(
                f"Impossibile eliminare l'asset: Sessione '{command.session_id}' non trovata."
            ) from e
        try:
            session.device.remove_asset(command.asset_id)
        except AssetNotFoundError as e:
            raise DeleteAssetFailure(
                f"Impossibile eliminare: Asset '{command.asset_id}' non trovato nel dispositivo."
            ) from e
        self._save_evaluation_session_port.save_evaluation_session(session)
