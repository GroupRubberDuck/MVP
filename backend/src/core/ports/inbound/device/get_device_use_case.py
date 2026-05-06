from abc import ABC, abstractmethod
from core.domain.evaluation_object.device import Device
class GetDeviceDetailCommand:
    def __init__(self, device_id: str) -> None:
        self.device_id = device_id


class GetDeviceDetailUseCase(ABC):
    @abstractmethod
    def get_device_detail(self, command: GetDeviceDetailCommand) -> Device: ...