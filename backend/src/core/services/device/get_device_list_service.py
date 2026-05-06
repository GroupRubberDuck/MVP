from core.ports.inbound.device.get_device_list_use_case import GetDeviceListUseCase
from core.ports.outbound.device.find_all_device_port import FindAllDevicePort, DeviceSummary


class GetDeviceListService(GetDeviceListUseCase):
    def __init__(self, find_all_device_port: FindAllDevicePort) -> None:
        self._find_all_device_port = find_all_device_port

    def get_device_list(self) -> list[DeviceSummary]:
        return self._find_all_device_port.find_all()