from core.ports.inbound.device.exceptions import DeleteDeviceFailure
from core.ports.inbound.device.delete_device_use_case import (
    DeleteDeviceCommand,
    DeleteDeviceUseCase,
)
from core.ports.outbound.device.exceptions import DeviceNotFoundError
from core.ports.outbound.device.delete_device_port import DeleteDevicePort


class DeleteDeviceService(DeleteDeviceUseCase):
    def __init__(self, delete_device_port: DeleteDevicePort) -> None:
        self._delete_device_port = delete_device_port

    def delete_device(self, command: DeleteDeviceCommand) -> None:
        try:
            self._delete_device_port.delete(command.device_id)
        except DeviceNotFoundError:
            raise DeleteDeviceFailure(
                f"Impossibile eliminare: dispositivo con ID '{command.device_id}' non trovato."
            )
