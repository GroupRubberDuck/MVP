from abc import abstractmethod
from src.core.ports.outbound.device.file_device_exporter_port import FileDeviceExporterPort
from src.core.services.device.device_file_command import DeviceFileCommand


class FileDeviceExporter(FileDeviceExporterPort):

    def generate_device_file(self, device_dto: DeviceFileCommand) -> bytes:
        self._prepare_structure(device_dto)
        self._write_data(device_dto)
        return self._finalize_output()

    @abstractmethod
    def _prepare_structure(self, device_dto: DeviceFileCommand) -> None: ...

    @abstractmethod
    def _write_data(self, device_dto: DeviceFileCommand) -> None: ...

    @abstractmethod
    def _finalize_output(self) -> bytes: ...