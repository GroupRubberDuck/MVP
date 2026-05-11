import pytest

from adapters.outbound.device.importer.concrete_file_device_importer_factory import ConcreteFileDeviceImporterFactory
from adapters.outbound.device.importer.json_file_device_importer import JSONFileDeviceImporter
from adapters.outbound.device.importer.csv_file_device_importer import CSVFileDeviceImporter
from adapters.outbound.device.importer.xml_file_device_importer import XMLFileDeviceImporter
from core.services.device.allowed_device_extensions import AllowedDeviceFileExtension


@pytest.fixture
def factory() -> ConcreteFileDeviceImporterFactory:
    return ConcreteFileDeviceImporterFactory()


class TestConcreteFileDeviceImporterFactory:

    def test_returns_json_importer(self, factory):
        assert isinstance(
            factory.get_file_device_importer(AllowedDeviceFileExtension.JSON),
            JSONFileDeviceImporter,
        )

    def test_returns_csv_importer(self, factory):
        assert isinstance(
            factory.get_file_device_importer(AllowedDeviceFileExtension.CSV),
            CSVFileDeviceImporter,
        )

    def test_returns_xml_importer(self, factory):
        assert isinstance(
            factory.get_file_device_importer(AllowedDeviceFileExtension.XML),
            XMLFileDeviceImporter,
        )