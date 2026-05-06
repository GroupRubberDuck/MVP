from core.ports.inbound.asset.update_asset_use_case import (
    UpdateAssetCommand,
    UpdateAssetUseCase,
)
from core.ports.outbound.evaluation.session_cache_port import (
    GetSessionPort,
    SaveSessionPort,
)

class UpdateAssetService(UpdateAssetUseCase):
    def __init__(
        self,
        get_session_port: GetSessionPort,
        save_session_port: SaveSessionPort,
    ) -> None:
        self._get_session_port = get_session_port
        self._save_session_port = save_session_port

    def update_asset(self, update_command: UpdateAssetCommand) -> None:
        session = self._get_session_port.get(update_command.session_id)
        updated_asset = session.get_asset(update_command.asset_id).update_anagraphic(
            name=update_command.name,
            asset_type=update_command.type,
            description=update_command.description,
        )
        session.update_asset(updated_asset)
        self._save_session_port.save(session)