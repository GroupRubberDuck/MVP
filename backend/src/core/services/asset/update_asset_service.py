from core.ports.inbound.asset.update_asset_use_case import (
    UpdateAssetCommand,
    UpdateAssetUseCase,
)
from core.ports.outbound.evaluation.get_session_port import GetSessionPort
from core.ports.outbound.evaluation.save_session_port import SaveSessionPort
from core.ports.inbound.asset.exceptions import UpdateAssetFailure
from core.ports.outbound.evaluation.exceptions import SessionNotFoundError
from core.domain.evaluation_object.exceptions import AssetNotFoundError


class UpdateAssetService(UpdateAssetUseCase):
    def __init__(
        self,
        get_session_port: GetSessionPort,
        save_session_port: SaveSessionPort,
    ) -> None:
        self._get_session_port = get_session_port
        self._save_session_port = save_session_port

    def update_asset(self, update_command: UpdateAssetCommand) -> None:
        try:
            session = self._get_session_port.get_session(update_command.session_id)
        except SessionNotFoundError as e:
            raise UpdateAssetFailure(
                f"Impossibile aggiornare l'asset: Sessione '{update_command.session_id}' non trovata."
            ) from e
        
        try: 
            updated_asset = session.device.get_asset(update_command.asset_id).update_anagraphic(
                name=update_command.name,
                asset_type=update_command.type,
                description=update_command.description,
            )
        except AssetNotFoundError as e:
            raise UpdateAssetFailure(
                f"Impossibile aggiornare: Asset '{update_command.asset_id}' non trovato."
            ) from e
        except ValueError as e:
            raise UpdateAssetFailure(f"Dati non validi per l'asset: {str(e)}") from e
        
        session.device.update_asset(updated_asset)
        self._save_session_port.save_session(session)
