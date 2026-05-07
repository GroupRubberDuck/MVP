import pytest
from flask import Flask
from src.adapters.inbound.device.download_file_controller import DownloadFileController


@pytest.fixture
def app():
    # Crea un'app Flask di test — necessaria per il contesto di risposta
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app


def test_restituisce_response(app):
    # Il risultato deve essere una Response Flask
    with app.app_context():
        response = DownloadFileController.build_file_response(b"bytes", "file.json")
        assert response is not None

def test_body_contiene_bytes_corretti(app):
    # Il body della risposta deve contenere i bytes passati
    with app.app_context():
        response = DownloadFileController.build_file_response(b"contenuto", "file.json")
        assert response.data == b"contenuto"

def test_mimetype_corretto(app):
    # Il mimetype deve essere application/octet-stream
    with app.app_context():
        response = DownloadFileController.build_file_response(b"bytes", "file.json")
        assert response.mimetype == "application/octet-stream"

def test_content_disposition_contiene_filename(app):
    # Il Content-Disposition deve contenere il filename corretto
    with app.app_context():
        response = DownloadFileController.build_file_response(b"bytes", "device-1.json")
        assert "device-1.json" in response.headers["Content-Disposition"]

def test_content_disposition_e_attachment(app):
    # Il Content-Disposition deve essere di tipo attachment
    with app.app_context():
        response = DownloadFileController.build_file_response(b"bytes", "file.json")
        assert "attachment" in response.headers["Content-Disposition"]