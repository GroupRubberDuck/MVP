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
        response = client.post("/api/devices/import")
        assert response.status_code == 400

    def test_returns_400_when_filename_is_empty(self, client):
        response = client.post(
            "/api/devices/import",
            data={"file": (io.BytesIO(b"{}"), "")},
            content_type="multipart/form-data",
        )
        assert response.status_code == 400

    def test_returns_400_when_extension_not_supported(self, client):
        response = _post_file(client, "device.txt")
        assert response.status_code == 400

    def test_returns_400_when_no_extension(self, client):
        response = _post_file(client, "device")
        assert response.status_code == 400

    def test_returns_201_when_import_succeeds(self, client, mock_service):
        mock_service.import_device.return_value = None
        response = _post_file(client, "device.json")
        assert response.status_code == 201
        assert "successo" in response.get_json()["message"]

    def test_calls_service_with_correct_extension(self, client, mock_service):
        mock_service.import_device.return_value = None
        _post_file(client, "device.json")
        command = mock_service.import_device.call_args[0][0]
        from core.services.device.allowed_device_extensions import AllowedDeviceFileExtension
        assert command.extension == AllowedDeviceFileExtension.JSON

    def test_returns_422_on_import_device_failure(self, client, mock_service):
        mock_service.import_device.side_effect = ImportDeviceFailure("File non valido.")
        response = _post_file(client, "device.json")
        assert response.status_code == 422
        assert "File non valido." in response.get_json()["error"]

    def test_returns_409_on_device_registration_failure(self, client, mock_service):
        mock_service.import_device.side_effect = DeviceRegistrationFailure("Dispositivo già esistente.")
        response = _post_file(client, "device.json")
        assert response.status_code == 409
        assert "già esistente" in response.get_json()["error"]