import pytest

from adapters.outbound.device.importer.concrete_file_device_importer_factory import (
    ConcreteFileDeviceImporterFactory,
)
from adapters.outbound.device.importer.json_file_device_importer import (
    JSONFileDeviceImporter,
)
from adapters.outbound.device.importer.csv_file_device_importer import (
    CSVFileDeviceImporter,
)
from adapters.outbound.device.importer.xml_file_device_importer import (
    XMLFileDeviceImporter,
)
from core.services.device.allowed_device_extensions import AllowedDeviceFileExtension


@pytest.fixture
def factory() -> ConcreteFileDeviceImporterFactory:
    return ConcreteFileDeviceImporterFactory()


class TestConcreteFileDeviceImporterFactory:
    def test_returns_json_importer(self, factory):
        """
        Data una richiesta di un importer per file con estensione JSON tramite l'enum AllowedDeviceFileExtension (Given),
        quando la factory viene invocata con il metodo get_file_device_importer (When),
        allora deve restituire un'istanza concreta di JSONFileDeviceImporter, correttamente tipizzata e pronta all'uso (Then).
        """
        assert isinstance(
            factory.get_file_device_importer(AllowedDeviceFileExtension.JSON),
            JSONFileDeviceImporter,
        )

    def test_returns_csv_importer(self, factory):
        """
        Data la necessità di importare dispositivi da un file in formato CSV (Given),
        quando si richiede l'importer corrispondente alla factory passando AllowedDeviceFileExtension.CSV (When),
        allora il metodo deve istanziare e restituire un oggetto di tipo CSVFileDeviceImporter (Then).
        """
        assert isinstance(
            factory.get_file_device_importer(AllowedDeviceFileExtension.CSV),
            CSVFileDeviceImporter,
        )

    def test_returns_xml_importer(self, factory):
        """
        Data la selezione del formato XML come sorgente per l'importazione dei dispositivi (Given),
        quando la factory elabora la richiesta con l'estensione AllowedDeviceFileExtension.XML (When),
        allora deve fornire un'implementazione concreta di XMLFileDeviceImporter, garantendo il supporto al parsing XML (Then).
        """
        assert isinstance(
            factory.get_file_device_importer(AllowedDeviceFileExtension.XML),
            XMLFileDeviceImporter,
        )
