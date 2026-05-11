from abc import ABC, abstractmethod
from core.domain.evaluation_object.device import Device


class FindDevicePort(ABC):
    @abstractmethod
    def find_by_id(self, device_id: str) -> Device: ...