import pytest
from unittest.mock import Mock

from core.ports.inbound.device.exceptions import DeleteDeviceFailure
from core.ports.inbound.device.delete_device_use_case import DeleteDeviceCommand
from core.ports.outbound.device.exceptions import DeviceNotFoundError
from core.ports.outbound.device.repository.delete_device_port import DeleteDevicePort
from core.services.device.delete_device_service import DeleteDeviceService


@pytest.fixture
def mock_delete_device_port(mocker) -> Mock:
    return mocker.Mock(spec=DeleteDevicePort)


@pytest.fixture
def service(mock_delete_device_port) -> DeleteDeviceService:
    return DeleteDeviceService(delete_device_port=mock_delete_device_port)


class TestDeleteDeviceService:

    def test_delete_device_success(
        self,
        service: DeleteDeviceService,
        mock_delete_device_port: Mock
    ):
        """
        Scenario: Il dispositivo esiste e viene eliminato senza errori.
        Risultato Atteso: La porta in uscita viene chiamata con l'ID corretto.
        """
        command = DeleteDeviceCommand(device_id="DEV-999")

        service.delete_device(command)

        mock_delete_device_port.delete.assert_called_once_with("DEV-999")

    def test_delete_device_raises_failure_when_not_found(
        self,
        service: DeleteDeviceService,
        mock_delete_device_port: Mock
    ):
        """
        Scenario: L'ID del dispositivo non esiste nel database.
        Risultato Atteso: Il service intercetta DeviceNotFoundError e lancia DeleteDeviceFailure.
        """
        command = DeleteDeviceCommand(device_id="DEV-GHOST")
        
        mock_delete_device_port.delete.side_effect = DeviceNotFoundError("Documento non trovato")

        with pytest.raises(DeleteDeviceFailure) as exc_info:
            service.delete_device(command)

        assert "DEV-GHOST" in str(exc_info.value)
        assert "Impossibile eliminare" in str(exc_info.value)
        
        mock_delete_device_port.delete.assert_called_once_with("DEV-GHOST")