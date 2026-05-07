import pytest
from unittest.mock import MagicMock
from flask import Flask
from src.adapters.inbound.device.export_device_controller import ExportDeviceController
from src.core.domain.evaluation_object.allowed_device_file_extension import AllowedDeviceFileExtension


@pytest.fixture
def export_uc_mock():
    mock = MagicMock()
    mock.export.return_value = b"file_bytes"
    return mock

@pytest.fixture
def app(export_uc_mock):
    # Crea l'app Flask di test con il blueprint del controller registrato
    app = Flask(__name__)
    app.config["TESTING"] = True
    controller = ExportDeviceController(export_uc=export_uc_mock)
    app.register_blueprint(controller.blueprint)
    return app

@pytest.fixture
def client(app):
    # Client di test Flask — simula le richieste HTTP
    return app.test_client()


# caso nominale

def test_export_risponde_200(client):
    # Una richiesta valida deve rispondere con status 200
    response = client.get("/api/devices/device-1/export?extension=json")
    assert response.status_code == 200

def test_export_risponde_con_bytes(client):
    # Il body della risposta deve contenere i bytes del file
    response = client.get("/api/devices/device-1/export?extension=json")
    assert response.data == b"file_bytes"

def test_export_content_disposition_contiene_filename(client):
    # Il Content-Disposition deve contenere il nome del file
    response = client.get("/api/devices/device-1/export?extension=json")
    assert "device_device-1.json" in response.headers["Content-Disposition"]

def test_export_chiama_service_con_command_corretto(client, export_uc_mock):
    # Il controller deve chiamare export con il command corretto
    client.get("/api/devices/device-1/export?extension=json")
    call_args = export_uc_mock.export.call_args[0][0]
    assert call_args.device_id == "device-1"
    assert call_args.extension == AllowedDeviceFileExtension.JSON

def test_export_usa_json_come_default(client, export_uc_mock):
    # Se non viene passata l'extension deve usare json come default
    client.get("/api/devices/device-1/export")
    call_args = export_uc_mock.export.call_args[0][0]
    assert call_args.extension == AllowedDeviceFileExtension.JSON


# casi di errore 

def test_export_extension_non_valida_risponde_400(client):
    # Un'extension non supportata deve rispondere con status 400
    response = client.get("/api/devices/device-1/export?extension=pdf")
    assert response.status_code == 400

def test_export_device_non_trovato_risponde_404(app, export_uc_mock):
    # Se il device non esiste deve rispondere con status 404
    export_uc_mock.export.side_effect = KeyError("Device non trovato")
    client = app.test_client()
    response = client.get("/api/devices/device-1/export?extension=json")
    assert response.status_code == 404