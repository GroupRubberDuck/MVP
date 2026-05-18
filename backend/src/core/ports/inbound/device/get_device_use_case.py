from abc import ABC, abstractmethod
from core.domain.evaluation_object.device import Device
from pydantic import BaseModel


class GetDeviceDetailCommand(BaseModel):
    model_config = {"frozen": True}
    device_id: str


class GetDeviceDetailUseCase(ABC):
    @abstractmethod
    def get_device_detail(self, command: GetDeviceDetailCommand) -> Device: ...
