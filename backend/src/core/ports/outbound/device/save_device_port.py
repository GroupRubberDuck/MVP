from abc import ABC, abstractmethod
from core.domain.evaluation_object.device import Device


class SaveDevicePort(ABC):
    @abstractmethod
    def save(self, device: Device) -> None: ...