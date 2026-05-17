import io
import pytest
from unittest.mock import MagicMock
from flask import Flask, Blueprint

from adapters.inbound.device.flask_import_device_controller import FlaskImportDeviceController
from core.ports.inbound.device.exceptions import DeviceRegistrationFailure, ImportDeviceFailure


@pytest.fixture
def mock_service():
    return MagicMock()


@pytest.fixture
def client(mock_service):
    app = Flask(__name__)
    app.config["TESTING"] = True

    controller = FlaskImportDeviceController(mock_service)
    bp = Blueprint("devices", __name__)
    controller.register_routes(bp)
    app.register_blueprint(bp)

    return app.test_client()


def _post_file(client, filename, content=b"{}"):
    return client.post(
        "/api/devices/import",
        data={"file": (io.BytesIO(content), filename)},
        content_type="multipart/form-data",
    )


class TestImportDeviceController:

    def test_returns_400_when_no_file_in_request(self, client):
        """
        Dato un payload di richiesta privo di qualsiasi file allegato (Given),
        quando viene invocato l'endpoint di importazione (When),
        allora il controller deve rifiutare l'operazione restituendo uno status 400 Bad Request (Then).
        """
        response = client.post("/api/devices/import")
        assert response.status_code == 400

    def test_returns_400_when_filename_is_empty(self, client):
        """
        Dato un payload contenente la chiave 'file' ma con un nome file vuoto (Given),
        quando il controller valida la richiesta (When),
        allora deve restituire uno status 400 Bad Request (Then).
        """
        response = client.post(
            "/api/devices/import",
            data={"file": (io.BytesIO(b"{}"), "")},
            content_type="multipart/form-data",
        )
        assert response.status_code == 400

    def test_returns_400_when_extension_not_supported(self, client):
        """
        Dato un file con un'estensione non prevista dal sistema (es. '.txt') (Given),
        quando l'utente tenta di importarlo (When),
        allora il controller deve bloccare il processo restituendo uno status 400 Bad Request (Then).
        """
        response = _post_file(client, "device.txt")
        assert response.status_code == 400

    def test_returns_400_when_no_extension(self, client):
        """
        Dato un file completamente privo di estensione nel nome (Given),
        quando viene sottomesso per l'importazione (When),
        allora il controller deve restituire uno status 400 Bad Request (Then).
        """
        response = _post_file(client, "device")
        assert response.status_code == 400

    def test_returns_201_when_import_succeeds(self, client, mock_service):
        """
        Dato un file supportato e strutturato correttamente (Given),
        quando il servizio esegue l'importazione con successo (When),
        allora il controller deve rispondere con uno status 201 Created e un messaggio di conferma (Then).
        """
        mock_service.import_device.return_value = None
        response = _post_file(client, "device.json")
        assert response.status_code == 201
        assert "successo" in response.get_json()["message"]

    def test_calls_service_with_correct_extension(self, client, mock_service):
        """
        Dato un file di cui è garantito il supporto (es. file JSON) (Given),
        quando il controller delega l'operazione di parsing (When),
        allora deve mappare correttamente l'estensione nell'enum relativo all'interno del Command per il servizio (Then).
        """
        mock_service.import_device.return_value = None
        _post_file(client, "device.json")
        command = mock_service.import_device.call_args[0][0]
        from core.services.device.allowed_device_extensions import AllowedDeviceFileExtension
        assert command.extension == AllowedDeviceFileExtension.JSON

    def test_returns_422_on_import_device_failure(self, client, mock_service):
        """
        Dato un file il cui parsing o validazione logica fallisce sollevando un'eccezione ImportDeviceFailure (Given),
        quando viene elaborato (When),
        allora il controller deve intercettare l'errore e rispondere con uno status 422 Unprocessable Entity (Then).
        """
        mock_service.import_device.side_effect = ImportDeviceFailure("File non valido.")
        response = _post_file(client, "device.json")
        assert response.status_code == 422
        assert "File non valido." in response.get_json()["error"]

    def test_returns_409_on_device_registration_failure(self, client, mock_service):
        """
        Dato un file sintatticamente valido ma che causa un conflitto a database (es. ID già esistente) sollevando una DeviceRegistrationFailure (Given),
        quando si tenta il salvataggio (When),
        allora il controller deve rispondere con uno status 409 Conflict (Then).
        """
        mock_service.import_device.side_effect = DeviceRegistrationFailure("Dispositivo già esistente.")
        response = _post_file(client, "device.json")
        assert response.status_code == 409
        assert "già esistente" in response.get_json()["error"]