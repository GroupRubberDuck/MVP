import io
import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace
from flask import Flask, Blueprint

from adapters.inbound.report.report_controller import FlaskExportReportController
from core.ports.inbound.report.exceptions import ExportReportFailure


@pytest.fixture
def mock_use_case():
    return MagicMock()


@pytest.fixture
def client(mock_use_case):
    app = Flask(__name__)
    app.config["TESTING"] = True

    controller = FlaskExportReportController(
        generate_report_use_case=mock_use_case,
    )
    bp = Blueprint("report", __name__)
    controller.register_routes(bp)
    app.register_blueprint(bp)

    return app.test_client()


def _make_exported_file(content=b"%PDF-fake", filename="device_report.pdf", media_type="application/pdf"):
    return SimpleNamespace(
        content=io.BytesIO(content),
        filename=filename,
        media_type=media_type,
    )


class TestExportReportSuccess:

    def test_returns_200_on_success(self, client, mock_use_case):
        mock_use_case.export_report.return_value = _make_exported_file()
        response = client.get("/sessions/S-1/devices/D-1/report/pdf")
        assert response.status_code == 200

    def test_returns_correct_content_type(self, client, mock_use_case):
        mock_use_case.export_report.return_value = _make_exported_file()
        response = client.get("/sessions/S-1/devices/D-1/report/pdf")
        assert response.content_type == "application/pdf"

    def test_returns_file_content(self, client, mock_use_case):
        mock_use_case.export_report.return_value = _make_exported_file(
            content=b"test-content"
        )
        response = client.get("/sessions/S-1/devices/D-1/report/pdf")
        assert response.data == b"test-content"

    def test_calls_use_case_with_correct_command(self, client, mock_use_case):
        mock_use_case.export_report.return_value = _make_exported_file()
        client.get("/sessions/S-1/devices/D-1/report/pdf")

        mock_use_case.export_report.assert_called_once()
        command = mock_use_case.export_report.call_args[0][0]
        assert command.session_id == "S-1"
        assert command.device_id == "D-1"
        assert command.report_format == "pdf"

    def test_response_has_download_filename(self, client, mock_use_case):
        mock_use_case.export_report.return_value = _make_exported_file(
            filename="Smart_Thermostat_report.pdf"
        )
        response = client.get("/sessions/S-1/devices/D-1/report/pdf")
        assert "Smart_Thermostat_report.pdf" in response.headers.get(
            "Content-Disposition", ""
        )


class TestExportReportFailures:

    def test_returns_422_on_export_failure(self, client, mock_use_case):
        mock_use_case.export_report.side_effect = ExportReportFailure(
            "Sessione non trovata."
        )
        response = client.get("/sessions/S-1/devices/D-1/report/pdf")
        assert response.status_code == 422
        assert "Sessione non trovata" in response.get_json()["error"]

    def test_returns_422_on_generation_error(self, client, mock_use_case):
        mock_use_case.export_report.side_effect = ExportReportFailure(
            "Errore durante la generazione del report."
        )
        response = client.get("/sessions/S-1/devices/D-1/report/pdf")
        assert response.status_code == 422
        assert "generazione" in response.get_json()["error"]