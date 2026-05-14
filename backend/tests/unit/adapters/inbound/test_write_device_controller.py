import pytest
from unittest.mock import Mock, patch
from flask import Flask, Blueprint

from adapters.inbound.device.flask_write_device_controller import FlaskWriteDeviceController
from core.ports.inbound.device.exceptions import (
    CreateDeviceFailure,
    UpdateDeviceFailure,
    DeleteDeviceFailure,
)

@pytest.fixture
def mock_create_use_case():
    return Mock()


@pytest.fixture
def mock_update_use_case():
    return Mock()


@pytest.fixture
def mock_delete_use_case():
    return Mock()


@pytest.fixture
def client(mock_create_use_case, mock_update_use_case, mock_delete_use_case):
    app = Flask(__name__)
    app.config["TESTING"] = True

    controller = FlaskWriteDeviceController(
        create_device_use_case=mock_create_use_case,
        update_device_use_case=mock_update_use_case,
        delete_device_use_case=mock_delete_use_case,
    )
    bp = Blueprint("devices", __name__)
    controller.register_routes(bp)
    
    @bp.route("/devices/<device_id>", endpoint="get_device_detail", methods=["GET"])
    def dummy_get_device_detail(device_id):
        return "Dummy route"
    app.register_blueprint(bp)

    return app.test_client()


# ── Create Device ──


class TestCreateDevice:
    @patch("adapters.inbound.device.flask_write_device_controller.url_for")
    def test_returns_201_on_success(self,mock_url_for, client, mock_create_use_case):
        mock_create_use_case.create_device.return_value = "D-123"
        mock_url_for.return_value = "/devices/D-123"
        response = client.post(
            "/devices",
            json={
                "device_name": "Test",
                "device_os": "Linux",
                "device_description": "A device",
                "standard_id": "STD-001",
            },
        )
        assert response.status_code == 201
        assert response.get_json()["device_id"] == "D-123"

    def test_calls_use_case_with_correct_data(self, client, mock_create_use_case):
        mock_create_use_case.create_device.return_value = "D-123"
        client.post(
            "/devices",
            json={
                "device_name": "Test",
                "device_os": "Linux",
                "device_description": "A device",
                "standard_id": "STD-001",
            },
        )
        command = mock_create_use_case.create_device.call_args[0][0]
        assert command.device_name == "Test"
        assert command.device_os == "Linux"
        assert command.device_description == "A device"
        assert command.standard_id == "STD-001"

    def test_returns_400_when_body_is_none(self, client):
        response = client.post("/devices", content_type="application/json")
        assert response.status_code == 400

    def test_returns_400_when_field_missing(self, client):
        response = client.post(
            "/devices",
            json={"device_name": "Test"},
        )
        assert response.status_code == 400

    def test_returns_error_on_create_failure(self, client, mock_create_use_case):
        mock_create_use_case.create_device.side_effect = CreateDeviceFailure("duplicato")
        response = client.post(
            "/devices",
            json={
                "device_name": "Test",
                "device_os": "Linux",
                "device_description": "A device",
                "standard_id": "STD-001",
            },
        )
        assert response.status_code == 409
        assert "duplicato" in response.get_json()["error"]


# ── Update Device ──


class TestUpdateDevice:

    def test_returns_200_on_success(self, client, mock_update_use_case):
        response = client.put(
            "/devices/D-1",
            json={
                "device_name": "Updated",
                "device_os": "Windows",
                "device_description": "Updated desc",
            },
        )
        assert response.status_code == 200

    def test_calls_use_case_with_correct_data(self, client, mock_update_use_case):
        client.put(
            "/devices/D-1",
            json={
                "device_name": "Updated",
                "device_os": "Windows",
                "device_description": "Updated desc",
            },
        )
        command = mock_update_use_case.update_device.call_args[0][0]
        assert command.device_id == "D-1"
        assert command.device_name == "Updated"
        assert command.device_os == "Windows"
        assert command.device_description == "Updated desc"

    def test_returns_400_when_body_is_none(self, client):
        response = client.put("/devices/D-1", content_type="application/json")
        assert response.status_code == 400

    def test_returns_400_when_field_missing(self, client):
        response = client.put(
            "/devices/D-1",
            json={"device_name": "Updated"},
        )
        assert response.status_code == 400

    def test_returns_error_on_update_failure(self, client, mock_update_use_case):
        mock_update_use_case.update_device.side_effect = UpdateDeviceFailure("non trovato")
        response = client.put(
            "/devices/D-1",
            json={
                "device_name": "Updated",
                "device_os": "Windows",
                "device_description": "Updated desc",
            },
        )
        assert response.status_code == 404
        assert "non trovato" in response.get_json()["error"]


# ── Delete Device ──


class TestDeleteDevice:

    def test_returns_204_on_success(self, client, mock_delete_use_case):
        response = client.delete("/devices/D-1")
        assert response.status_code == 204

    def test_calls_use_case_with_correct_id(self, client, mock_delete_use_case):
        client.delete("/devices/D-1")
        command = mock_delete_use_case.delete_device.call_args[0][0]
        assert command.device_id == "D-1"

    def test_returns_error_on_delete_failure(self, client, mock_delete_use_case):
        mock_delete_use_case.delete_device.side_effect = DeleteDeviceFailure("non trovato")
        response = client.delete("/devices/D-1")
        assert response.status_code == 404
        assert "non trovato" in response.get_json()["error"]