from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class DeleteDeviceCommand:
    device_id: str


class DeleteDeviceUseCase(ABC):
    @abstractmethod
    def delete_device(self, command: DeleteDeviceCommand) -> None: ...