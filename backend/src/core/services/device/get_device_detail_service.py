from core.ports.inbound.device.get_device_use_case import GetDeviceDetailCommand, GetDeviceDetailUseCase


from core.ports.outbound.device.repository.find_device_port import FindDevicePort 

from core.domain.evaluation_object.device import Device

from core.ports.outbound.device.exceptions import DeviceNotFoundError 
from core.ports.inbound.device.exceptions import DeviceNotFoundFailure 

class GetDeviceDetailService(GetDeviceDetailUseCase):
    def __init__(self, find_device_port: FindDevicePort) -> None:
        self._find_device_port = find_device_port

    def get_device_detail(self, command: GetDeviceDetailCommand)-> Device:
        try:
                return self._find_device_port.find_by_id(command.device_id)
        except DeviceNotFoundError as e:
                raise DeviceNotFoundFailure(f"Dispositivo con id {command.device_id} non trovato.") from e