import pytest
from io import BytesIO
from unittest.mock import MagicMock

from core.domain.shared.exceptions import DomainError
from core.ports.inbound.report.exceptions import ExportReportFailure
from core.ports.inbound.report.generate_report_use_case import GenerateReportCommand
from core.ports.outbound.evaluation.exceptions import EvaluationSessionNotFoundError
from core.services.report.generate_report_service import GenerateReportService
from core.domain.evaluation_engine.evaluation_detail import DeviceEvaluationDetail
from core.ports.inbound.report.generate_report_use_case import ReportFormat


@pytest.fixture
def mock_session_port():
    return MagicMock()


@pytest.fixture
def mock_report_generator():
    return MagicMock()


@pytest.fixture
def mock_engine():
    return MagicMock()


@pytest.fixture
def service(mock_session_port, mock_report_generator, mock_engine):
    return GenerateReportService(
        get_evaluation_session_port=mock_session_port,
        report_generator_port=mock_report_generator,
        evaluation_engine=mock_engine,
    )


@pytest.fixture
def command():
    return GenerateReportCommand(
        session_id="SESSION-1", device_id="DEV-1", report_format=ReportFormat.PDF
    )


def _setup_happy_path(mock_session_port, mock_engine, mock_report_generator, command):

    mock_tree = MagicMock()
    mock_tree.nodes = {"n1": {"node_id": "n1", "question": "test?"}}

    mock_req = MagicMock()
    mock_req.requirement_id = "REQ-1"
    mock_req.name = "Req Test"
    mock_req.description = "Descrizione"
    mock_req.target_description = "Target"
    mock_req.decision_tree = mock_tree

    mock_standard = MagicMock()
    mock_standard.id = "STD-1"
    mock_standard.get_requirement.return_value = mock_req

    mock_anagraphic = MagicMock()
    mock_anagraphic.name = "Asset Test"
    mock_anagraphic.asset_type = "Hardware"
    mock_anagraphic.description = "Descrizione asset"

    mock_asset = MagicMock()
    mock_asset.id = "ASSET-1"
    mock_asset.anagraphic = mock_anagraphic

    mock_device = MagicMock()
    mock_device.id = "DEV-1"
    mock_device.name = "Device Test"
    mock_device.os = "Linux"
    mock_device.description = "Descrizione device"
    mock_device.get_asset.return_value = mock_asset

    mock_session = MagicMock()
    mock_session.device = mock_device
    mock_session.standard = mock_standard
    mock_session_port.get_evaluation_session.return_value = mock_session

    mock_req_result = MagicMock()
    mock_req_result.requirement_id = "REQ-1"
    mock_req_result.justification = "Tutto ok"
    mock_req_result.node_choices = {"n1": True}
    mock_req_result.state = "PASS"
    mock_req_result.dependencies = []

    mock_asset_result = MagicMock()
    mock_asset_result.asset_id = "ASSET-1"
    mock_asset_result.verdict = "PASS"
    mock_asset_result.requirement_results = [mock_req_result]

    mock_device_result = MagicMock()
    mock_device_result.verdict = "PASS"
    mock_device_result.asset_results = [mock_asset_result]

    mock_engine.evaluate.return_value = mock_device_result

    fake_file = BytesIO(b"PDF CONTENT")
    mock_report_generator.generate_report.return_value = fake_file

    return mock_req


class TestExportReportSuccess:
    def test_generates_and_returns_report_successfully(
        self, service, mock_session_port, mock_engine, mock_report_generator, command
    ):
        """
        Dato un comando di generazione report valido per una sessione esistente (Given),
        quando il servizio esegue la procedura di esportazione (When),
        allora deve restituire il contenuto del file generato (es. PDF) correttamente prodotto dal generatore di report (Then).
        """
        _setup_happy_path(
            mock_session_port, mock_engine, mock_report_generator, command
        )

        result = service.export_report(command)

        assert result.content.read() == b"PDF CONTENT"

    def test_builds_correct_device_evaluation_detail(
        self, service, mock_session_port, mock_engine, mock_report_generator, command
    ):
        """
        Dati i risultati della valutazione ottenuti dal motore di dominio (Given),
        quando il servizio prepara i dati per l'esportazione (When),
        allora deve costruire un oggetto DeviceEvaluationDetail accurato e passarlo al generatore di report,
        includendo le anagrafiche e i verdetti corretti per device, asset e requisiti (Then).
        """

        _setup_happy_path(
            mock_session_port, mock_engine, mock_report_generator, command
        )

        service.export_report(command)

        mock_report_generator.generate_report.assert_called_once()
        args, _ = mock_report_generator.generate_report.call_args
        detail_passed_to_generator = args[0]

        assert isinstance(detail_passed_to_generator, DeviceEvaluationDetail)
        assert detail_passed_to_generator.device_id == "DEV-1"
        assert detail_passed_to_generator.name == "Device Test"
        assert detail_passed_to_generator.verdict == "PASS"

        assert len(detail_passed_to_generator.asset_details) == 1
        asset_detail = detail_passed_to_generator.asset_details[0]
        assert asset_detail.asset_id == "ASSET-1"
        assert asset_detail.name == "Asset Test"

        assert len(asset_detail.requirement_details) == 1
        req_detail = asset_detail.requirement_details[0]
        assert req_detail.requirement_id == "REQ-1"
        assert req_detail.state == "PASS"


class TestExportReportFailures:
    def test_raises_failure_when_session_not_found(
        self, service, mock_session_port, command
    ):
        """
        Dato un ID sessione non presente nel sistema (Given),
        quando viene richiesta la generazione del report (When),
        allora il servizio deve sollevare un'eccezione ExportReportFailure indicando che la sessione non è stata trovata (Then).
        """
        mock_session_port.get_evaluation_session.side_effect = (
            EvaluationSessionNotFoundError()
        )

        with pytest.raises(ExportReportFailure, match="SESSION-1"):
            service.export_report(command)

    def test_raises_failure_on_domain_error_during_evaluation(
        self, service, mock_session_port, mock_engine, mock_report_generator, command
    ):
        """
        Dato un errore di business logica durante la fase di valutazione (es. un ciclo infinito nell'albero decisionale) (Given),
        quando il motore di valutazione solleva un DomainError (When),
        allora il servizio deve catturare l'eccezione tecnica e rilanciarla come ExportReportFailure per l'utente (Then).
        """
        _setup_happy_path(
            mock_session_port, mock_engine, mock_report_generator, command
        )

        mock_engine.evaluate.side_effect = DomainError(
            "Ciclo infinito rilevato nell'albero"
        )

        with pytest.raises(ExportReportFailure, match="Ciclo infinito"):
            service.export_report(command)

    # il decision tree non è vuoto teoricamente parlando
    # def test_raises_failure_when_requirement_has_no_decision_tree(
    # self, service, mock_session_port, mock_engine, mock_report_generator, command
    # ):
    # mock_req = _setup_happy_path(mock_session_port, mock_engine, mock_report_generator, command)
    #
    # mock_req.decision_tree = None


#
# with pytest.raises(ExportReportFailure, match="non ha un albero decisionale"):
# service.export_report(command)
