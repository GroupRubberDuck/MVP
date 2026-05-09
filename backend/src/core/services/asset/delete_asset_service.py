from core.ports.inbound.asset.exceptions import DeleteAssetFailure
from core.ports.inbound.asset.delete_asset_use_case import (
    DeleteAssetCommand,
    DeleteAssetUseCase,
)
<<<<<<< HEAD
from core.ports.outbound.evaluation.get_session_port import GetSessionPort
from core.ports.outbound.evaluation.save_session_port import SaveSessionPort
=======
from core.ports.outbound.evaluation.session_cache_port import (
    GetSessionPort,
    SaveSessionPort,
)
>>>>>>> origin
from core.ports.outbound.evaluation.exceptions import SessionNotFoundError
from core.domain.evaluation_object.exceptions import AssetNotFoundError


class DeleteAssetService(DeleteAssetUseCase):
    def __init__(
        self,
        save_session_port: SaveSessionPort,
        get_session_port: GetSessionPort,
    ) -> None:
        self._save_session_port = save_session_port
        self._get_session_port = get_session_port

    def delete_asset(self, command: DeleteAssetCommand) -> None:
        try:
            session = self._get_session_port.get_session(command.session_id)
        except SessionNotFoundError as e:
            raise DeleteAssetFailure(
                f"Impossibile eliminare l'asset: Sessione '{command.session_id}' non trovata."
            ) from e
        try:
            session.device.remove_asset(command.asset_id)
        except AssetNotFoundError as e:
            raise DeleteAssetFailure(
                f"Impossibile eliminare: Asset '{command.asset_id}' non trovato nel dispositivo."
            ) from e
<<<<<<< HEAD
        self._save_session_port.save_session(session)
=======
        self._save_session_port.save(session)
>>>>>>> origin
