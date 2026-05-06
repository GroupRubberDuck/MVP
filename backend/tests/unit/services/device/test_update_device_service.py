import pytest
from unittest.mock import Mock

from core.ports.inbound.device.exceptions import UpdateDeviceFailure
from core.ports.inbound.device.update_device_anagraphic_use_case import UpdateDeviceCommand
from core.ports.outbound.device.exceptions import DeviceNotFoundError
from core.ports.outbound.device.find_device_port import FindDevicePort
from core.ports.outbound.device.save_device_port import SaveDevicePort
from core.services.device.update_device_service import UpdateDeviceService


@pytest.fixture
def mock_find_device_port(mocker) -> Mock:
    return mocker.Mock(spec=FindDevicePort)


@pytest.fixture
def mock_save_device_port(mocker) -> Mock:
    return mocker.Mock(spec=SaveDevicePort)


@pytest.fixture
def service(mock_find_device_port, mock_save_device_port) -> UpdateDeviceService:
    return UpdateDeviceService(
        find_device_port=mock_find_device_port,
        save_device_port=mock_save_device_port
    )


class TestUpdateDeviceService:

    def test_update_device_success(
        self,
        service: UpdateDeviceService,
        mock_find_device_port: Mock,
        mock_save_device_port: Mock,
        mocker
    ):
        """
        Scenario: Il dispositivo esiste.
        Risultato Atteso: I campi vengono aggiornati e il dispositivo viene salvato.
        """
        
        command = UpdateDeviceCommand(
            device_id="DEV-123",
            device_name="Nuovo Router",
            device_os="OpenWRT",
            device_description="Router aggiornato"
        )
        
        mock_device = mocker.Mock()
        mock_find_device_port.find_by_id.return_value = mock_device

        service.update_device(command)

        mock_find_device_port.find_by_id.assert_called_once_with("DEV-123")
        
        mock_device.update_info.assert_called_once_with(
            name="Nuovo Router",
            os="OpenWRT",
            description="Router aggiornato"
        )
        
        mock_save_device_port.save.assert_called_once_with(mock_device)

    def test_update_device_raises_failure_when_not_found(
        self,
        service: UpdateDeviceService,
        mock_find_device_port: Mock,
        mock_save_device_port: Mock
    ):
        """
        Scenario: Il dispositivo richiesto non esiste nel database.
        Risultato Atteso: Viene sollevata un'eccezione di dominio UpdateDeviceFailure e non viene salvato nulla.
        """
        command = UpdateDeviceCommand(
            device_id="DEV-INVALID",
            device_name="Nome",
            device_os="OS",
            device_description="Desc"
        )
        
        mock_find_device_port.find_by_id.side_effect = DeviceNotFoundError("Non trovato")

        with pytest.raises(UpdateDeviceFailure) as exc_info:
            service.update_device(command)

        assert "DEV-INVALID" in str(exc_info.value)
        
        mock_save_device_port.save.assert_not_called()