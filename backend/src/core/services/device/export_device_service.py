from core.ports.inbound.device.export_device_use_case import ExportDeviceUseCase
from core.ports.outbound.device.repository.find_device_port import FindDevicePort
from core.ports.outbound.device.exporter.file_device_exporter_factory_port import (
    FileDeviceExporterFactoryPort,
)
from core.ports.inbound.device.export_device_use_case import (
    ExportDeviceCommand,
    ExportedFile,
)
from core.ports.outbound.device.exceptions import DeviceNotFoundError, DeviceExportError
from core.ports.inbound.device.exceptions import (
    DeviceNotFoundFailure,
    ExportDeviceFailure,
)


class ExportDeviceService(ExportDeviceUseCase):
    def __init__(
        self,
        find_device: FindDevicePort,
        exporter_factory: FileDeviceExporterFactoryPort,
    ):
        self._find_device = find_device
        self._exporter_factory = exporter_factory

    def export_device(self, export_command: ExportDeviceCommand) -> ExportedFile:

        try:
            device = self._find_device.find_by_id(export_command.device_id)
        except DeviceNotFoundError:
            raise DeviceNotFoundFailure("Device not found")

        exporter = self._exporter_factory.get_file_device_exporter(
            export_command.extension
        )
        try:
            content = exporter.generate_device_file(device)
        except DeviceExportError:
            raise ExportDeviceFailure("Failed to generate export file")

        return ExportedFile(
            content=content,
            filename=f"device_{export_command.device_id}.{export_command.extension.value}",
            media_type=export_command.extension.media_type,
        )
