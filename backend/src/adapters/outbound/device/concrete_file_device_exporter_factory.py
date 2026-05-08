from core.ports.outbound.device.file_device_exporter_factory_port import FileDeviceExporterFactoryPort
from core.ports.outbound.device.file_device_exporter_port import FileDeviceExporterPort
from core.domain.evaluation_object.allowed_device_file_extension import AllowedDeviceFileExtension
from adapters.outbound.device.xml_file_device_exporter import XMLFileDeviceExporter
from adapters.outbound.device.json_file_device_exporter import JSONFileDeviceExporter
from adapters.outbound.device.csv_file_device_exporter import CSVFileDeviceExporter


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