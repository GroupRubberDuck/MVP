import pytest
from unittest.mock import Mock, patch
from flask import Flask

from core.ports.inbound.device.exceptions import DeviceNotFoundFailure
from core.ports.inbound.compliance_standard.exceptions import StandardNotFoundFailure

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




# ── FlaskQueryDeviceController ──


class TestFlaskQueryDeviceControllerList:

    @patch("adapters.inbound.device.flask_query_device_controller.render_template")
    def test_get_device_list_renders_template(
        self, mock_render, client, mock_get_device_list_use_case
    ):
        
        device1 = Mock()
        device1.device_id = "D-1"
        device1.name = "Device 1"

        device2 = Mock()
        device2.device_id = "D-2"
        device2.name = "Device 2"
        mock_get_device_list_use_case.get_device_list.return_value = [
            device1,
            device2,
        ]
        mock_render.return_value = "html"

        response = client.get("/devices")

        assert response.status_code == 200
        mock_render.assert_called_once()
        template_name = mock_render.call_args[0][0]
        assert template_name == "layouts/device/device_list.html"

        devices_arg = mock_render.call_args[1]["devices"]
        assert len(devices_arg) == 2
        assert devices_arg[0].device_id == "D-1"
        assert devices_arg[1].device_id == "D-2"

    @patch("adapters.inbound.device.flask_query_device_controller.render_template")
    def test_get_device_list_empty(
        self, mock_render, client, mock_get_device_list_use_case
    ):
        mock_get_device_list_use_case.get_device_list.return_value = []
        mock_render.return_value = "html"

        response = client.get("/devices")

        assert response.status_code == 200
        devices_arg = mock_render.call_args[1]["devices"]
        assert devices_arg == []


class TestFlaskQueryDeviceControllerDetail:

    @patch("adapters.inbound.device.flask_query_device_controller.render_template")
    def test_get_device_detail_renders_template(
        self,
        mock_render,
        client,
        mock_get_device_detail_use_case,
        mock_get_compliance_standard_use_case,
    ):
        mock_device = Mock()
        mock_device.id = "D-1"
        mock_device.name = "Device 1"
        mock_device.os = "Linux"
        mock_device.description = "Test device"
        mock_device.standard_id = "STD-1"
        mock_get_device_detail_use_case.get_device_detail.return_value = mock_device

        mock_standard = Mock()
        mock_standard.name = "EN 303 645"
        mock_standard.version_number = "1.0"
        mock_get_compliance_standard_use_case.get_compliance_standard.return_value = (
            mock_standard
        )
        mock_render.return_value = "html"

        response = client.get("/devices/D-1")

        assert response.status_code == 200
        mock_render.assert_called_once()
        template_name = mock_render.call_args[0][0]
        assert template_name == "layouts/device/device_detail.html"

        device_dto = mock_render.call_args[1]["device"]
        assert device_dto.device_id == "D-1"
        assert device_dto.compliance_standard_name == "EN 303 645"
        assert device_dto.compliance_standard_version == "1.0"

    @patch("adapters.inbound.device.flask_query_device_controller.render_template")
    def test_device_not_found_returns_404(
        self, mock_render, client, mock_get_device_detail_use_case
    ):
        mock_get_device_detail_use_case.get_device_detail.side_effect = (
            DeviceNotFoundFailure("non trovato")
        )
        mock_render.return_value = "html"

        response = client.get("/devices/D-999")

        assert response.status_code == 404
        template_name = mock_render.call_args[0][0]
        assert template_name == "error.html"

    @patch("adapters.inbound.device.flask_query_device_controller.render_template")
    def test_standard_not_found_returns_404(
        self,
        mock_render,
        client,
        mock_get_device_detail_use_case,
        mock_get_compliance_standard_use_case,
    ):
        mock_device = Mock()
        mock_device.id = "D-1"
        mock_device.standard_id = "STD-999"
        mock_get_device_detail_use_case.get_device_detail.return_value = mock_device

        mock_get_compliance_standard_use_case.get_compliance_standard.side_effect = (
            StandardNotFoundFailure("standard non trovato")
        )
        mock_render.return_value = "html"

        response = client.get("/devices/D-1")

        assert response.status_code == 404
        template_name = mock_render.call_args[0][0]
        assert template_name == "error.html"