import pytest
import io
from unittest.mock import MagicMock
from flask import Flask, blueprints
from adapters.inbound.device.flask_export_device_controller import (
    FlaskExportDeviceController,
)
from core.domain.evaluation_object.allowed_device_file_extension import (
    AllowedDeviceFileExtension,
)
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
    """
    Verifica che richiedendo l'esportazione di un device esistente in formato JSON (When),
    il controller restituisca uno status code 200 OK (Then).
    """
    response = client.get("/api/devices/device-1/export?extension=json")
    assert response.status_code == 200


def test_export_risponde_con_bytes(client):
    """
    Verifica che richiedendo l'esportazione di un device (When),
    il corpo della risposta contenga esattamente i byte generati dall'use case (Then).
    """
    response = client.get("/api/devices/device-1/export?extension=json")
    assert response.data == b"file_bytes"


def test_export_content_disposition_contiene_filename(client):
    """
    Verifica che richiedendo l'esportazione (When),
    l'header Content-Disposition della risposta contenga il nome del file corretto
    passato dall'use case per forzarne il download (Then).
    """
    response = client.get("/api/devices/device-1/export?extension=json")
    assert "device_device-1.json" in response.headers["Content-Disposition"]


def test_export_chiama_service_con_command_corretto(client, export_uc_mock):
    """
    Verifica che richiedendo l'esportazione con una specifica estensione (When),
    il controller mappi correttamente i parametri nel Command
    e lo passi all'use case (Then).
    """
    client.get("/api/devices/device-1/export?extension=json")
    call_args = export_uc_mock.export_device.call_args[0][0]
    assert call_args.device_id == "device-1"
    assert call_args.extension == AllowedDeviceFileExtension.JSON


def test_export_usa_json_come_default(client, export_uc_mock):
    """
    Verifica che richiedendo l'esportazione senza specificare l'estensione (When),
    il controller imposti di default il formato JSON nel Command passato all'use case (Then).
    """
    client.get("/api/devices/device-1/export")
    call_args = export_uc_mock.export_device.call_args[0][0]
    assert call_args.extension == AllowedDeviceFileExtension.JSON


# === CASI DI ERRORE ===


def test_export_extension_non_valida_risponde_400(client):
    """
    Dato un formato di esportazione non supportato,
    verifica che richiedendo l'esportazione (When),
    il controller blocchi la richiesta restituendo uno status code 400 Bad Request (Then).
    """
    response = client.get("/api/devices/device-1/export?extension=pdf")
    assert response.status_code == 400


def test_export_device_non_trovato_risponde_404(app, export_uc_mock):
    """
    Dato un ID device inesistente che genera una DeviceNotFoundFailure nell'use case,
    verifica che richiedendo l'esportazione (When),
    il controller gestisca l'eccezione restituendo uno status code 404 Not Found (Then).
    """
    export_uc_mock.export_device.side_effect = DeviceNotFoundFailure(
        "Device non trovato"
    )
    client = app.test_client()
    response = client.get("/api/devices/device-1/export?extension=json")
    assert response.status_code == 404
