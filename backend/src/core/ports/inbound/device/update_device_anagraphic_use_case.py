from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class UpdateDeviceCommand:
    device_id: str
    device_name: str
    device_os: str
    device_description: str


class UpdateDeviceUseCase(ABC):
    @abstractmethod
    def update_device(self, command: UpdateDeviceCommand) -> None: ...