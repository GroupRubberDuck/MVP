from abc import ABC, abstractmethod
from pydantic import BaseModel


class UpdateDeviceCommand(BaseModel):
    device_id: str
    device_name: str
    device_os: str
    device_description: str


class UpdateDeviceUseCase(ABC):
    @abstractmethod
    def update_device(self, command: UpdateDeviceCommand) -> None: ...