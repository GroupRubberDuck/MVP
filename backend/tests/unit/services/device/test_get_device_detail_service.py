import pytest
from unittest.mock import Mock, patch
from flask import Flask

from core.domain.evaluation_object.device_summary import DeviceSummary
from core.ports.inbound.device.get_device_use_case import GetDeviceDetailCommand
from core.ports.inbound.device.exceptions import DeviceNotFoundFailure
from core.ports.inbound.compliance_standard.exceptions import StandardNotFoundFailure
from core.ports.outbound.device.exceptions import DeviceNotFoundError

from core.services.device.get_device_list_service import GetDeviceListService
from core.services.device.get_device_detail_service import GetDeviceDetailService
from adapters.inbound.device.flask_query_device_controller import FlaskQueryDeviceController


# ── Fixtures ──


@pytest.fixture
def mock_find_all_port():
    return Mock()


@pytest.fixture
def mock_find_device_port():
    return Mock()


@pytest.fixture
def mock_get_device_list_use_case():
    return Mock()


@pytest.fixture
def mock_get_device_detail_use_case():
    return Mock()


@pytest.fixture
def mock_get_compliance_standard_use_case():
    return Mock()


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(
    app,
    mock_get_device_list_use_case,
    mock_get_device_detail_use_case,
    mock_get_compliance_standard_use_case,
):
    from flask import Blueprint

    controller = FlaskQueryDeviceController(
        get_device_list_use_case=mock_get_device_list_use_case,
        get_device_detail_use_case=mock_get_device_detail_use_case,
        get_compliance_standard_use_case=mock_get_compliance_standard_use_case,
    )
    bp = Blueprint("devices", __name__)
    controller.register_routes(bp)
    app.register_blueprint(bp)

    return app.test_client()




# ── GetDeviceDetailService ──


class TestGetDeviceDetailService:

    def test_returns_device_from_port(self, mock_find_device_port):
        mock_device = Mock()
        mock_device.id = "D-1"
        mock_find_device_port.find_by_id.return_value = mock_device

        service = GetDeviceDetailService(mock_find_device_port)
        command = GetDeviceDetailCommand(device_id="D-1")
        result = service.get_device_detail(command)

        assert result.id == "D-1"
        mock_find_device_port.find_by_id.assert_called_once_with("D-1")

    def test_raises_failure_when_device_not_found(self, mock_find_device_port):
        mock_find_device_port.find_by_id.side_effect = DeviceNotFoundError("non trovato")

        service = GetDeviceDetailService(mock_find_device_port)
        command = GetDeviceDetailCommand(device_id="D-999")

        with pytest.raises(DeviceNotFoundFailure, match="D-999"):
            service.get_device_detail(command)

    def test_failure_wraps_original_error(self, mock_find_device_port):
        original = DeviceNotFoundError("non trovato")
        mock_find_device_port.find_by_id.side_effect = original

        service = GetDeviceDetailService(mock_find_device_port)
        command = GetDeviceDetailCommand(device_id="D-999")

        with pytest.raises(DeviceNotFoundFailure) as exc_info:
            service.get_device_detail(command)
        assert exc_info.value.__cause__ is original
