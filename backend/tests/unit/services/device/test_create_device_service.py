import pytest
from unittest.mock import Mock
from core.services.device.create_device_service import CreateDeviceService
from core.ports.inbound.device.create_device_use_case import CreateDeviceCommand
from core.ports.inbound.device.exceptions import CreateDeviceFailure
from core.ports.outbound.device.exceptions import DuplicateDeviceError


@pytest.fixture
def mock_register_port():
    return Mock()


@pytest.fixture
def service(mock_register_port):
    return CreateDeviceService(register_device_port=mock_register_port)


@pytest.fixture
def command():
    return CreateDeviceCommand(
        device_name="Test Device",
        device_os="Linux",
        device_description="A test device",
        standard_id="STD-001",
    )


class TestCreateDeviceService:

    def test_returns_device_id(self, service, command):
        result = service.create_device(command)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_calls_register_with_device(self, service, mock_register_port, command):
        service.create_device(command)
        mock_register_port.register.assert_called_once()
        device = mock_register_port.register.call_args[0][0]
        assert device.name == "Test Device"
        assert device.os == "Linux"
        assert device.description == "A test device"
        assert device.standard_id == "STD-001"

    def test_device_has_generated_id(self, service, mock_register_port, command):
        service.create_device(command)
        device = mock_register_port.register.call_args[0][0]
        assert device.id is not None
        assert len(device.id) > 0

    def test_returned_id_matches_device_id(self, service, mock_register_port, command):
        result = service.create_device(command)
        device = mock_register_port.register.call_args[0][0]
        assert result == device.id

    def test_each_call_generates_unique_id(self, service, command):
        id1 = service.create_device(command)
        id2 = service.create_device(command)
        assert id1 != id2

    def test_raises_failure_on_duplicate(self, service, mock_register_port, command):
        mock_register_port.register.side_effect = DuplicateDeviceError("duplicato")

        with pytest.raises(CreateDeviceFailure):
            service.create_device(command)

    def test_failure_wraps_original_error(self, service, mock_register_port, command):
        original = DuplicateDeviceError("duplicato")
        mock_register_port.register.side_effect = original

        with pytest.raises(CreateDeviceFailure) as exc_info:
            service.create_device(command)
        assert exc_info.value.__cause__ is original

    def test_device_created_with_no_assets(self, service, mock_register_port, command):
        service.create_device(command)
        device = mock_register_port.register.call_args[0][0]
        assert len(device.assets) == 0