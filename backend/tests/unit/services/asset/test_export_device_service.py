import pytest
from unittest.mock import MagicMock
from core.services.device.export_device_service import ExportDeviceService, ExportedFile
from core.ports.inbound.device.export_device_use_case import ExportDeviceCommand
from core.domain.evaluation_object.allowed_device_file_extension import AllowedDeviceFileExtension
from core.domain.evaluation_object.device import Device


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

def test_export_restituisce_file(service, valid_command):
    """
    Dato un comando di esportazione valido (Given),
    quando il servizio esegue l'esportazione (When),
    allora deve restituire un oggetto ExportedFile che incapsula i dati generati (Then).
    """
    # Verifica che il service incarti il risultato in un oggetto ExportedFile
    result = service.export_device(valid_command)
    assert isinstance(result, ExportedFile)

def test_export_restituisce_output_dell_exporter(service, valid_command):
    """
    Dato un comando di esportazione (Given),
    quando l'exporter genera i byte del file (When),
    allora il contenuto dell'oggetto ExportedFile restituito deve coincidere esattamente con l'output dell'exporter (Then).
    """
    # Il contenuto del file esportato deve coincidere con quello generato dall'exporter
    result = service.export_device(valid_command)
    assert result.content == b"file_bytes"

def test_export_chiama_find_by_id_con_device_id_corretto(service, valid_command, find_device_mock):
    """
    Dato un identificativo di dispositivo presente nel comando (Given),
    quando il servizio avvia l'esportazione (When),
    allora deve invocare il metodo find_by_id del repository utilizzando l'ID corretto (Then).
    """
    # find_by_id deve essere chiamato con il device_id del command
    service.export_device(valid_command)
    find_device_mock.find_by_id.assert_called_once_with("device-1")

def test_export_chiama_factory_con_extension_corretta(service, valid_command, exporter_factory_mock):
    """
    Dato un formato di estensione richiesto nel comando (Given),
    quando il servizio richiede un exporter (When),
    allora la factory deve essere invocata con l'estensione corretta per fornire il modulo di esportazione adeguato (Then).
    """
    # La factory deve essere chiamata con l'extension del command
    service.export_device(valid_command)
    exporter_factory_mock.get_file_device_exporter.assert_called_once_with(
        AllowedDeviceFileExtension.JSON
    )

def test_export_chiama_generate_device_file(service, valid_command, exporter_mock, device):
    """
    Dato un dispositivo recuperato dal sistema (Given),
    quando viene eseguita l'esportazione (When),
    allora l'exporter selezionato deve ricevere l'entità di dominio Device per generare il file finale (Then).
    """
    # L'exporter deve ricevere l'entità di dominio Device (grazie al nostro refactoring!)
    service.export_device(valid_command)
    exporter_mock.generate_device_file.assert_called_once_with(device)


# casi di errore

def test_export_device_non_trovato_lancia_keyerror(exporter_factory_mock):
    """
    Dato un comando con un ID dispositivo non esistente nel database (Given),
    quando il repository fallisce nel recupero (When),
    allora il servizio deve propagare l'eccezione KeyError (Then).
    """
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
        service.export_device(command)

def test_export_extension_non_supportata_lancia_valueerror(find_device_mock):
    """
    Dato un comando che richiede un'estensione non supportata dalla factory (Given),
    quando viene richiesto l'exporter (When),
    allora deve essere sollevata un'eccezione ValueError (Then).
    """
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
        service.export_device(command)