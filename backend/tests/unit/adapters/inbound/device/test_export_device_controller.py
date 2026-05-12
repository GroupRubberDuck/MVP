import pytest
import io
from unittest.mock import MagicMock
from flask import Flask, blueprints
from adapters.inbound.device.flask_export_device_controller import FlaskExportDeviceController
from core.domain.evaluation_object.allowed_device_file_extension import AllowedDeviceFileExtension
from core.ports.inbound.device.exceptions import DeviceNotFoundFailure


@pytest.fixture
def export_uc_mock():
    mock = MagicMock()
    mock_dto = MagicMock()

    mock_dto.content = io.BytesIO(b"file_bytes")
    mock_dto.filename = "device_device-1.json"
    mock.export_device.return_value = mock_dto
    
    return mock

@pytest.fixture
def app(export_uc_mock):
    # Crea l'app Flask di test con il blueprint del controller registrato
    app = Flask(__name__)
    app.config["TESTING"] = True
    blueprint = blueprints.Blueprint("devices", __name__)
    controller = FlaskExportDeviceController(export_device_use_case=export_uc_mock)
    controller.register_routes(blueprint)
    app.register_blueprint(blueprint)
    return app

@pytest.fixture
def client(app):
    # Client di test Flask — simula le richieste HTTP
    return app.test_client()


# === CASO NOMINALE ===

def test_export_risponde_200(client):
    response = client.get("/api/devices/device-1/export?extension=json")
    assert response.status_code == 200

def test_export_risponde_con_bytes(client):
    response = client.get("/api/devices/device-1/export?extension=json")
    assert response.data == b"file_bytes"

def test_export_content_disposition_contiene_filename(client):
    response = client.get("/api/devices/device-1/export?extension=json")
    assert "device_device-1.json" in response.headers["Content-Disposition"]

def test_export_chiama_service_con_command_corretto(client, export_uc_mock):
    client.get("/api/devices/device-1/export?extension=json")
    call_args = export_uc_mock.export_device.call_args[0][0]
    assert call_args.device_id == "device-1"
    assert call_args.extension == AllowedDeviceFileExtension.JSON

def test_export_usa_json_come_default(client, export_uc_mock):
    client.get("/api/devices/device-1/export")
    call_args = export_uc_mock.export_device.call_args[0][0]
    assert call_args.extension == AllowedDeviceFileExtension.JSON


# === CASI DI ERRORE ===

def test_export_extension_non_valida_risponde_400(client):
    response = client.get("/api/devices/device-1/export?extension=pdf")
    assert response.status_code == 400

def test_export_device_non_trovato_risponde_404(app, export_uc_mock):
    export_uc_mock.export_device.side_effect = DeviceNotFoundFailure("Device non trovato")
    client = app.test_client()
    response = client.get("/api/devices/device-1/export?extension=json")
    assert response.status_code == 404