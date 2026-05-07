from abc import ABC, abstractmethod
from ....services.device.export_device_command import ExportDeviceCommand


class ExportDeviceUseCase(ABC):

    @abstractmethod
    def export_device(self, export_command: ExportDeviceCommand) -> bytes: ...