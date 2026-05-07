from ...ports.inbound.device.export_device_use_case import ExportDeviceUseCase
from ...ports.outbound.device.find_device_port import FindDevicePort
from ...ports.outbound.device.file_device_exporter_factory_port import FileDeviceExporterFactoryPort
from .export_device_command import ExportDeviceCommand
from .device_file_command import DeviceFileCommand


class ExportDeviceService(ExportDeviceUseCase):

    def __init__(
        self,
        find_device: FindDevicePort,
        exporter_factory: FileDeviceExporterFactoryPort,
    ):
        self._find_device = find_device
        self._exporter_factory = exporter_factory

    def export(self, query: ExportDeviceCommand) -> bytes:
        # Recupera il device tramite FindDevicePort
        device = self._find_device.find_by_id(query.device_id)

        # Ottiene l'exporter corretto dalla factory — restituisce FileDeviceExporterPort
        exporter = self._exporter_factory.get_file_device_exporter(query.extension)

        # Genera e restituisce i bytes del file
        return exporter.generate_device_file(DeviceFileCommand(device=device))