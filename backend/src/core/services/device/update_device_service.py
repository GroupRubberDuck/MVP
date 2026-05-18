from core.ports.inbound.device.exceptions import UpdateDeviceFailure
from core.ports.inbound.device.update_device_use_case import (
    UpdateDeviceCommand,
    UpdateDeviceUseCase,
)
from core.ports.outbound.device.exceptions import DeviceNotFoundError
from core.ports.outbound.device.repository.find_device_port import FindDevicePort
from core.ports.outbound.device.repository.save_device_port import SaveDevicePort


class UpdateDeviceService(UpdateDeviceUseCase):
    def __init__(
        self, find_device_port: FindDevicePort, save_device_port: SaveDevicePort
    ) -> None:
        self._find_device_port = find_device_port
        self._save_device_port = save_device_port

    def update_device(self, command: UpdateDeviceCommand) -> None:
        try:
            device = self._find_device_port.find_by_id(command.device_id)
        except DeviceNotFoundError:
            raise UpdateDeviceFailure(
                f"Dispositivo con ID '{command.device_id}' non trovato."
            )

        device.update_info(
            name=command.device_name,
            os=command.device_os,
            description=command.device_description,
        )
        self._save_device_port.save_device(device)
