import pytest
from unittest.mock import MagicMock
from typing import BinaryIO

from core.ports.inbound.device.import_device_use_case import (
    AllowedDeviceFileExtension,
    ImportDeviceCommand,
)
from core.ports.outbound.device.file_device_importer_factory_port import FileDeviceImporterFactoryPort
from core.ports.outbound.device.file_device_importer_port import FileDeviceImporterPort
from core.ports.outbound.device.register_device_port import RegisterDevicePort
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

    def test_calls_factory_with_correct_extension(self, service, factory, importer, comando_csv):
        factory.get_file_device_importer.return_value = importer
        importer.parse_device_file.return_value = MagicMock()
        service.import_device(comando_csv)
        factory.get_file_device_importer.assert_called_once_with(AllowedDeviceFileExtension.CSV)

    def test_calls_importer_with_file_content(self, service, factory, importer, comando_csv):
        factory.get_file_device_importer.return_value = importer
        importer.parse_device_file.return_value = MagicMock()
        service.import_device(comando_csv)
        importer.parse_device_file.assert_called_once_with(comando_csv.device_file_content)

    def test_registers_device_returned_by_parser(self, service, factory, importer, register_port, comando_csv):
        device = MagicMock()
        factory.get_file_device_importer.return_value = importer
        importer.parse_device_file.return_value = device
        service.import_device(comando_csv)
        register_port.register.assert_called_once_with(device)

    def test_complete_flow_json(self, service, factory, importer, register_port):
        comando = ImportDeviceCommand(
            device_file_content=MagicMock(spec=BinaryIO),
            extension=AllowedDeviceFileExtension.JSON,
        )
        device = MagicMock()
        factory.get_file_device_importer.return_value = importer
        importer.parse_device_file.return_value = device
        service.import_device(comando)
        factory.get_file_device_importer.assert_called_once_with(AllowedDeviceFileExtension.JSON)
        register_port.register.assert_called_once_with(device)