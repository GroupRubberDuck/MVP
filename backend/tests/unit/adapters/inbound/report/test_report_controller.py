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


def _make_exported_file(
    content=b"%PDF-fake", filename="device_report.pdf", media_type="application/pdf"
):
    return SimpleNamespace(
        content=io.BytesIO(content),
        filename=filename,
        media_type=media_type,
    )


class TestExportReportSuccess:
    def test_returns_200_on_success(self, client, mock_use_case):
        """
        Dati dei parametri validi per l'esportazione di un report (Given),
        quando viene effettuata la richiesta GET all'endpoint di esportazione (When),
        allora il controller deve completare l'operazione e restituire uno status code 200 OK (Then).
        """
        mock_use_case.export_report.return_value = _make_exported_file()
        response = client.get("/sessions/S-1/devices/D-1/report/pdf")
        assert response.status_code == 200

    def test_returns_correct_content_type(self, client, mock_use_case):
        """
        Dato un report generato con successo in uno specifico formato (es. PDF) (Given),
        quando la risposta HTTP viene preparata (When),
        allora il controller deve impostare correttamente l'header Content-Type (es. 'application/pdf') (Then).
        """
        mock_use_case.export_report.return_value = _make_exported_file()
        response = client.get("/sessions/S-1/devices/D-1/report/pdf")
        assert response.content_type == "application/pdf"

    def test_returns_file_content(self, client, mock_use_case):
        """
        Dato un file in memoria generato dallo use case contenente determinati byte (Given),
        quando il client riceve la risposta (When),
        allora il corpo della risposta deve coincidere esattamente con i byte del file originario (Then).
        """
        mock_use_case.export_report.return_value = _make_exported_file(
            content=b"test-content"
        )
        response = client.get("/sessions/S-1/devices/D-1/report/pdf")
        assert response.data == b"test-content"

    def test_calls_use_case_with_correct_command(self, client, mock_use_case):
        """
        Dati ID di sessione, ID di device e formato desiderato presenti nell'URL (Given),
        quando il controller processa la richiesta (When),
        allora deve mappare correttamente questi parametri nel Command e invocare lo use case dedicato all'esportazione (Then).
        """
        mock_use_case.export_report.return_value = _make_exported_file()
        client.get("/sessions/S-1/devices/D-1/report/pdf")

        mock_use_case.export_report.assert_called_once()
        command = mock_use_case.export_report.call_args[0][0]
        assert command.session_id == "S-1"
        assert command.device_id == "D-1"
        assert command.report_format == "pdf"

    def test_response_has_download_filename(self, client, mock_use_case):
        """
        Dato un file di report a cui è stato assegnato un nome specifico (Given),
        quando la risposta viene inviata al client (When),
        allora l'header 'Content-Disposition' deve includere il nome del file corretto per forzarne il download (Then).
        """
        mock_use_case.export_report.return_value = _make_exported_file(
            filename="Smart_Thermostat_report.pdf"
        )
        response = client.get("/sessions/S-1/devices/D-1/report/pdf")
        assert "Smart_Thermostat_report.pdf" in response.headers.get(
            "Content-Disposition", ""
        )


class TestExportReportFailures:
    def test_returns_422_on_export_failure(self, client, mock_use_case):
        """
        Dato uno scenario in cui mancano dati fondamentali (es. sessione non trovata) che causa una ExportReportFailure (Given),
        quando viene richiesta l'esportazione del report (When),
        allora il controller deve gestire l'eccezione e restituire uno status 422 Unprocessable Entity con il messaggio di errore (Then).
        """
        mock_use_case.export_report.side_effect = ExportReportFailure(
            "Sessione non trovata."
        )
        response = client.get("/sessions/S-1/devices/D-1/report/pdf")
        assert response.status_code == 422
        assert "Sessione non trovata" in response.get_json()["error"]

    def test_returns_422_on_generation_error(self, client, mock_use_case):
        """
        Dato un errore interno sopraggiunto durante la fase logica di generazione del documento (Given),
        quando l'uso case fallisce (When),
        allora il controller deve intercettare l'errore e rispondere con uno status 422 Unprocessable Entity (Then).
        """
        mock_use_case.export_report.side_effect = ExportReportFailure(
            "Errore durante la generazione del report."
        )
        response = client.get("/sessions/S-1/devices/D-1/report/pdf")
        assert response.status_code == 422
        assert "generazione" in response.get_json()["error"]
