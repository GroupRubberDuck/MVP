from abc import ABC, abstractmethod
from pydantic import BaseModel


class CreateDeviceCommand(BaseModel):
    device_name: str
    device_os: str
    device_description: str
    standard_id: str


class CreateDeviceUseCase(ABC):
    @abstractmethod
    def create_device(self, command: CreateDeviceCommand) -> str: ...
