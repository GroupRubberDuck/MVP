import pytest
from unittest.mock import MagicMock
from typing import BinaryIO
from core.services.device.allowed_device_extensions import AllowedDeviceFileExtension

from core.ports.inbound.device.import_device_use_case import ImportDeviceCommand

from core.ports.outbound.device.importer.file_device_importer_factory_port import (
    FileDeviceImporterFactoryPort,
)
from core.ports.outbound.device.importer.file_device_importer_port import (
    FileDeviceImporterPort,
)
from core.ports.outbound.device.repository.register_device_port import (
    RegisterDevicePort,
)
from core.services.device.import_device_service import ImportDeviceService


@pytest.fixture
def factory() -> MagicMock:
    return MagicMock(spec=FileDeviceImporterFactoryPort)


@pytest.fixture
def importer() -> MagicMock:
    return MagicMock(spec=FileDeviceImporterPort)


@pytest.fixture
def register_port() -> MagicMock:
    return MagicMock(spec=RegisterDevicePort)


@pytest.fixture
def service(factory, register_port) -> ImportDeviceService:
    return ImportDeviceService(
        device_importer_factory=factory,
        register_device_port=register_port,
    )


@pytest.fixture
def comando_csv() -> ImportDeviceCommand:
    return ImportDeviceCommand(
        device_file_content=MagicMock(spec=BinaryIO),
        extension=AllowedDeviceFileExtension.CSV,
    )


class TestImportDevice:
    def test_calls_factory_with_correct_extension(
        self, service, factory, importer, comando_csv
    ):
        """
        Dato un comando di importazione per un file CSV (Given),
        quando il servizio processa la richiesta (When),
        allora deve interrogare la factory per ottenere l'importer specifico corrispondente all'estensione CSV (Then).
        """
        factory.get_file_device_importer.return_value = importer
        importer.parse_device_file.return_value = MagicMock()
        service.import_device(comando_csv)
        factory.get_file_device_importer.assert_called_once_with(
            AllowedDeviceFileExtension.CSV
        )

    def test_calls_importer_with_file_content(
        self, service, factory, importer, comando_csv
    ):
        """
        Dato un contenuto di file binario fornito nel comando (Given),
        quando l'importer viene recuperato dalla factory (When),
        allora il servizio deve invocare il parsing passando esattamente il contenuto del file ricevuto (Then).
        """
        factory.get_file_device_importer.return_value = importer
        importer.parse_device_file.return_value = MagicMock()
        service.import_device(comando_csv)
        importer.parse_device_file.assert_called_once_with(
            comando_csv.device_file_content
        )

    def test_registers_device_returned_by_parser(
        self, service, factory, importer, register_port, comando_csv
    ):
        """
        Dato un dispositivo correttamente deserializzato dal parser (Given),
        quando il processo di importazione prosegue (When),
        allora il servizio deve invocare la porta di registrazione per persistere l'entità Device nel sistema (Then).
        """
        device = MagicMock()
        factory.get_file_device_importer.return_value = importer
        importer.parse_device_file.return_value = device
        service.import_device(comando_csv)
        register_port.register.assert_called_once_with(device)

    def test_complete_flow_json(self, service, factory, importer, register_port):
        """
        Dato un comando di importazione per un file JSON (Given),
        quando viene eseguito l'intero flusso di importazione (When),
        allora il servizio deve orchestrare correttamente factory, importer JSON e repository per completare l'operazione (Then).
        """
        comando = ImportDeviceCommand(
            device_file_content=MagicMock(spec=BinaryIO),
            extension=AllowedDeviceFileExtension.JSON,
        )
        device = MagicMock()
        factory.get_file_device_importer.return_value = importer
        importer.parse_device_file.return_value = device
        service.import_device(comando)
        factory.get_file_device_importer.assert_called_once_with(
            AllowedDeviceFileExtension.JSON
        )
        register_port.register.assert_called_once_with(device)
