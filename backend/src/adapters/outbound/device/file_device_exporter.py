import io
from abc import ABC, abstractmethod
from core.ports.outbound.device.file_device_exporter_port import FileDeviceExporterPort
from core.domain.evaluation_object.device import Device
from typing import IO


class FileDeviceExporter(FileDeviceExporterPort, ABC):

    def generate_device_file(self, device: Device) -> IO[bytes]:
        self._prepare_structure(device)
        self._write_data(device)
        raw_bytes =  self._finalize_output()
        return io.BytesIO(raw_bytes)

    @abstractmethod
    def _prepare_structure(self, device: Device) -> None: ...

    @abstractmethod
    def _write_data(self, device: Device) -> None: ...

    @abstractmethod
    def _finalize_output(self) -> bytes: ...