import pytest
from unittest.mock import Mock

from core.ports.inbound.device.exceptions import UpdateDeviceFailure
from core.ports.inbound.device.update_device_use_case import UpdateDeviceCommand
from core.ports.outbound.device.exceptions import DeviceNotFoundError
from core.ports.outbound.device.repository.find_device_port import FindDevicePort
from core.ports.outbound.device.repository.save_device_port import SaveDevicePort
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
        Dato un identificativo di dispositivo esistente e nuovi dati anagrafici (Given),
        quando viene richiesto l'aggiornamento del dispositivo (When),
        allora il servizio deve recuperare l'entità dal repository, invocare i metodi di aggiornamento 
        del dominio e infine persistere le modifiche tramite la porta di salvataggio (Then).
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
        
        mock_save_device_port.save_device.assert_called_once_with(mock_device)

    def test_update_device_raises_failure_when_not_found(
        self,
        service: UpdateDeviceService,
        mock_find_device_port: Mock,
        mock_save_device_port: Mock
    ):
        """
        Dato un ID dispositivo non presente nel sistema (Given),
        quando il repository segnala che il dispositivo non è stato trovato (When),
        allora il servizio deve sollevare un'eccezione di dominio UpdateDeviceFailure e 
        garantire che non venga eseguito alcun tentativo di salvataggio (Then).
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
        
        mock_save_device_port.save_device.assert_not_called()