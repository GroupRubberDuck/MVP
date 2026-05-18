from core.ports.inbound.device.get_device_list_use_case import GetDeviceListUseCase
from core.ports.outbound.device.repository.find_all_devices_port import (
    FindAllDevicePort,
)
from core.domain.evaluation_object.device_summary import DeviceSummary


class GetDeviceListService(GetDeviceListUseCase):
    def __init__(self, find_all_device_port: FindAllDevicePort) -> None:
        self._find_all_device_port = find_all_device_port

    def get_device_list(self) -> list[DeviceSummary]:
        return self._find_all_device_port.find_all()
