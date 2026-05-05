from abc import ABC, abstractmethod
from core.domain.evaluation_object.device import Device


class RegisterDevicePort(ABC):
    @abstractmethod
    def register(self, device: Device) -> None: ...