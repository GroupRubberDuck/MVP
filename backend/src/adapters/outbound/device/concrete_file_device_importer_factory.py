from core.services.device.allowed_device_extensions import AllowedDeviceFileExtension
from core.ports.outbound.device.file_device_importer_factory_port import FileDeviceImporterFactoryPort
from core.ports.outbound.device.file_device_importer_port import FileDeviceImporterPort
from adapters.outbound.device.json_file_device_importer import JSONFileDeviceImporter
from adapters.outbound.device.csv_file_device_importer import CSVFileDeviceImporter
from adapters.outbound.device.xml_file_device_importer import XMLFileDeviceImporter


class ConcreteFileDeviceImporterFactory(FileDeviceImporterFactoryPort):

    def get_file_device_importer(
        self, extension: AllowedDeviceFileExtension
    ) -> FileDeviceImporterPort:
        match extension:
            case AllowedDeviceFileExtension.JSON:
                return JSONFileDeviceImporter()
            case AllowedDeviceFileExtension.CSV:
                return CSVFileDeviceImporter()
            case AllowedDeviceFileExtension.XML:
                return XMLFileDeviceImporter()