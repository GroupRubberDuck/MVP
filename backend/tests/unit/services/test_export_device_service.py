import pytest
from unittest.mock import MagicMock
from src.core.services.device.export_device_service import ExportDeviceService
from src.core.services.device.export_device_command import ExportDeviceCommand
from src.core.domain.evaluation_object.allowed_device_file_extension import AllowedDeviceFileExtension
from src.core.domain.evaluation_object.device import Device


# fixtures 

@pytest.fixture
def device():
    return Device.create(
        device_id="device-1",
        standard_id="standard-1",
        name="Test Device",
        os="Linux",
        description="Device di test",
    )

@pytest.fixture
def find_device_mock(device):
    mock = MagicMock()
    mock.find_by_id.return_value = device
    return mock

@pytest.fixture
def exporter_mock():
    # Mock dell'exporter concreto — restituisce bytes fittizi
    mock = MagicMock()
    mock.generate_device_file.return_value = b"file_bytes"
    return mock

@pytest.fixture
def exporter_factory_mock(exporter_mock):
    # Mock della factory — restituisce sempre l'exporter mock
    mock = MagicMock()
    mock.get_file_device_exporter.return_value = exporter_mock
    return mock

@pytest.fixture
def service(find_device_mock, exporter_factory_mock):
    return ExportDeviceService(
        find_device=find_device_mock,
        exporter_factory=exporter_factory_mock,
    )

@pytest.fixture
def valid_command():
    return ExportDeviceCommand(
        device_id="device-1",
        extension=AllowedDeviceFileExtension.JSON,
    )


# caso nominale

def test_export_restituisce_bytes(service, valid_command):
    # Il service deve restituire bytes
    result = service.export(valid_command)
    assert isinstance(result, bytes)

def test_export_chiama_find_by_id_con_device_id_corretto(service, valid_command, find_device_mock):
    # find_by_id deve essere chiamato con il device_id del command
    service.export(valid_command)
    find_device_mock.find_by_id.assert_called_once_with("device-1")

def test_export_chiama_factory_con_extension_corretta(service, valid_command, exporter_factory_mock):
    # La factory deve essere chiamata con l'extension del command
    service.export(valid_command)
    exporter_factory_mock.get_file_device_exporter.assert_called_once_with(
        AllowedDeviceFileExtension.JSON
    )

def test_export_chiama_generate_device_file(service, valid_command, exporter_mock):
    # L'exporter deve essere chiamato con il DeviceFileCommand
    service.export(valid_command)
    exporter_mock.generate_device_file.assert_called_once()

def test_export_restituisce_output_dell_exporter(service, valid_command):
    # Il risultato deve essere quello restituito dall'exporter
    result = service.export(valid_command)
    assert result == b"file_bytes"


# casi di errore

def test_export_device_non_trovato_lancia_keyerror(exporter_factory_mock):
    # Se il device non esiste find_by_id deve propagare KeyError
    find_device_mock = MagicMock()
    find_device_mock.find_by_id.side_effect = KeyError("Device non trovato")
    service = ExportDeviceService(
        find_device=find_device_mock,
        exporter_factory=exporter_factory_mock,
    )
    command = ExportDeviceCommand(
        device_id="device-inesistente",
        extension=AllowedDeviceFileExtension.JSON,
    )
    with pytest.raises(KeyError):
        service.export(command)

def test_export_extension_non_supportata_lancia_valueerror(find_device_mock):
    # Se l'extension non è supportata la factory deve propagare ValueError
    exporter_factory_mock = MagicMock()
    exporter_factory_mock.get_file_device_exporter.side_effect = ValueError("Formato non supportato")
    service = ExportDeviceService(
        find_device=find_device_mock,
        exporter_factory=exporter_factory_mock,
    )
    command = ExportDeviceCommand(
        device_id="device-1",
        extension=AllowedDeviceFileExtension.JSON,
    )
    with pytest.raises(ValueError):
        service.export(command)