from core.ports.inbound.device.import_device_use_case import (
    ImportDeviceCommand,
    ImportDeviceUseCase,
)

from core.ports.outbound.device.file_device_importer_factory_port import FileDeviceImporterFactoryPort
from core.ports.outbound.device.register_device_port import RegisterDevicePort


class ImportDeviceService(ImportDeviceUseCase):
    def __init__(
        self,
        device_importer_factory: FileDeviceImporterFactoryPort,
        register_device_port: RegisterDevicePort,
    ) -> None:
        self._device_importer_factory = device_importer_factory
        self._register_device_port = register_device_port

    def import_device(self, command: ImportDeviceCommand) -> None:
        importer = self._device_importer_factory.get_file_device_importer(
            command.extension
        )
        device = importer.parse_device_file(command.device_file_content)
        self._register_device_port.register(device)
