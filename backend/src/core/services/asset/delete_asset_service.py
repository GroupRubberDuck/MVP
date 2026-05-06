from core.ports.inbound.device.import_device_use_case import (
    DeleteAssetCommand,
    DeleteAssetUseCase,
)

class DeleteAssetService(DeleteAssetUseCase):
    def __init__(
        self,
        save_session_port: SaveSessionPort,
        get_session_port: GetSessionPort,
    ) -> None:
        self._save_session_port = save_session_port
        self._get_session_port = get_session_port

    def delete_asset(delete_command: DeleteAssetCommand) -> None:
        pass