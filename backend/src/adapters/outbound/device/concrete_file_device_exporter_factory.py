from src.core.ports.outbound.device.file_device_exporter_factory_port import FileDeviceExporterFactoryPort
from src.core.ports.outbound.device.file_device_exporter_port import FileDeviceExporterPort
from src.core.domain.evaluation_object.allowed_device_file_extension import AllowedDeviceFileExtension
from .xml_file_device_exporter import XMLFileDeviceExporter
from .json_file_device_exporter import JSONFileDeviceExporter
from .csv_file_device_exporter import CSVFileDeviceExporter


class ConcreteFileDeviceExporterFactory(FileDeviceExporterFactoryPort):

    _exporters = {
        AllowedDeviceFileExtension.XML: XMLFileDeviceExporter,
        AllowedDeviceFileExtension.JSON: JSONFileDeviceExporter,
        AllowedDeviceFileExtension.CSV: CSVFileDeviceExporter,
    }

    def get_file_device_exporter(
        self, extension: AllowedDeviceFileExtension
    ) -> FileDeviceExporterPort:
        cls = self._exporters.get(extension)
        if cls is None:
            raise ValueError(f"Formato non supportato: {extension}")
        return cls()