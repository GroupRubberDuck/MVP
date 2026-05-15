import pytest
from unittest.mock import MagicMock

from core.domain.evaluation_standard.evaluation_state import EvaluationState
from core.domain.evaluation_object.exceptions import AssetNotFoundError
from core.ports.inbound.asset.exceptions import GetAssetDetailFailure
from core.ports.inbound.asset.get_asset_evaluation_detail_use_case import GetAssetEvaluationDetailCommand
from core.ports.outbound.evaluation.exceptions import EvaluationSessionNotFoundError
from core.services.asset.get_asset_evaluation_detail_service import GetAssetEvaluationDetailService


@pytest.fixture
def mock_session_port():
    return MagicMock()


@pytest.fixture
def mock_engine():
    return MagicMock()


@pytest.fixture
def service(mock_session_port, mock_engine):
    return GetAssetEvaluationDetailService(
        get_evaluation_session_port=mock_session_port,
        evaluation_engine=mock_engine,
    )


@pytest.fixture
def command():
    return GetAssetEvaluationDetailCommand(device_id="DEVICE-1", asset_id="ASSET-1", session_id="SESSION-1")


def _make_mock_session(asset_id: str = "ASSET-1") -> MagicMock:
    mock_asset = MagicMock()
    mock_asset.id = asset_id
    mock_asset.anagraphic.name = "Network Interface"
    mock_asset.anagraphic.description = "Ethernet controller"

    mock_session = MagicMock()
    mock_session.device.get_asset.return_value = mock_asset
    return mock_session


def _make_mock_device_result(
    asset_id: str = "ASSET-1",
    verdict: EvaluationState = EvaluationState.PASS,
    requirement_results: tuple = (),
) -> MagicMock:
    mock_asset_result = MagicMock()
    mock_asset_result.asset_id = asset_id
    mock_asset_result.requirement_results = requirement_results
    mock_asset_result.verdict = verdict

    mock_device_result = MagicMock()
    mock_device_result.get_asset_result.return_value = mock_asset_result
    return mock_device_result


class TestGetAssetDetail:

    def test_returns_asset_detail_with_correct_id(
        self, service, mock_session_port, mock_engine, command
    ):
        """
        Dato un identificativo asset valido (Given),
        quando viene richiesto il dettaglio valutativo dell'asset (When),
        allora il DTO restituito deve contenere l'asset_id corretto (Then).
        """
        mock_session_port.get_evaluation_session.return_value = _make_mock_session()
        mock_engine.evaluate.return_value = _make_mock_device_result()

        result = service.get_asset(command)

        assert result.asset_id == "ASSET-1"

    def test_returns_asset_detail_with_correct_name(
        self, service, mock_session_port, mock_engine, command
    ):
        """
        Dato un asset con nome 'Network Interface' (Given),
        quando si recupera il dettaglio (When),
        allora il nome nel DTO risultante deve corrispondere a quello dell'anagrafica (Then).
        """
        mock_session_port.get_evaluation_session.return_value = _make_mock_session()
        mock_engine.evaluate.return_value = _make_mock_device_result()

        result = service.get_asset(command)

        assert result.name == "Network Interface"

    def test_returns_asset_detail_with_pass_verdict(
        self, service, mock_session_port, mock_engine, command
    ):
        """
        Dato un motore di valutazione che restituisce un verdetto PASS per l'asset (Given),
        quando il servizio processa la richiesta (When),
        allora il verdetto nel dettaglio finale deve essere EvaluationState.PASS (Then).
        """
        mock_session_port.get_evaluation_session.return_value = _make_mock_session()
        mock_engine.evaluate.return_value = _make_mock_device_result(verdict=EvaluationState.PASS)

        result = service.get_asset(command)

        assert result.verdict == EvaluationState.PASS

    def test_returns_asset_detail_with_fail_verdict(
        self, service, mock_session_port, mock_engine, command
    ):
        """
        Dato un verdetto FAIL emesso dal motore (Given),
        quando viene generato il dettaglio (When),
        allora lo stato finale dell'asset deve riflettere EvaluationState.FAIL (Then).
        """
        mock_session_port.get_evaluation_session.return_value = _make_mock_session()
        mock_engine.evaluate.return_value = _make_mock_device_result(verdict=EvaluationState.FAIL)

        result = service.get_asset(command)

        assert result.verdict == EvaluationState.FAIL

    def test_returns_empty_requirement_details_when_no_requirements(
        self, service, mock_session_port, mock_engine, command
    ):
        """
        Dato un asset senza risultati di requisiti associati (Given),
        quando viene costruito il DTO di dettaglio (When),
        allora la lista dei requirement_details deve risultare vuota (Then).
        """
        mock_session_port.get_evaluation_session.return_value = _make_mock_session()
        mock_engine.evaluate.return_value = _make_mock_device_result(requirement_results=())

        result = service.get_asset(command)

        assert result.requirement_details == ()

    def test_calls_port_with_correct_session_id(
        self, service, mock_session_port, mock_engine, command
    ):
        """
        Dato un ID sessione nel comando (Given),
        quando il servizio avvia il recupero (When),
        allora deve interrogare la porta della sessione con l'ID fornito (Then).
        """
        mock_session_port.get_evaluation_session.return_value = _make_mock_session()
        mock_engine.evaluate.return_value = _make_mock_device_result()

        service.get_asset(command)

        mock_session_port.get_evaluation_session.assert_called_once_with("SESSION-1")

    def test_calls_engine_with_session_device_and_standard(
        self, service, mock_session_port, mock_engine, command
    ):
        """
        Data una sessione valida recuperata con successo (Given),
        quando viene invocata la valutazione (When),
        allora il motore di valutazione deve ricevere esattamente il device e lo standard della sessione (Then).
        """
        mock_session = _make_mock_session()
        mock_session_port.get_evaluation_session.return_value = mock_session
        mock_engine.evaluate.return_value = _make_mock_device_result()

        service.get_asset(command)

        mock_engine.evaluate.assert_called_once_with(
            mock_session.device, mock_session.standard
        )

    def test_calls_device_result_with_correct_asset_id(
        self, service, mock_session_port, mock_engine, command
    ):
        """
        Dato il risultato globale della valutazione del dispositivo (Given),
        quando il servizio deve isolare l'asset specifico (When),
        allora deve estrarre il risultato dell'asset utilizzando l'identificativo corretto dal risultato aggregato (Then).
        """
        mock_session_port.get_evaluation_session.return_value = _make_mock_session()
        mock_device_result = _make_mock_device_result()
        mock_engine.evaluate.return_value = mock_device_result

        service.get_asset(command)

        mock_device_result.get_asset_result.assert_called_once_with("ASSET-1")


class TestGetAssetDetailFailures:

    def test_raises_failure_when_session_not_found(
        self, service, mock_session_port, command
    ):
        """
        Dato un ID sessione non esistente (Given),
        quando viene richiesto il dettaglio dell'asset (When),
        allora deve essere sollevata un'eccezione GetAssetDetailFailure riportando l'ID della sessione (Then).
        """
        mock_session_port.get_evaluation_session.side_effect = EvaluationSessionNotFoundError()

        with pytest.raises(GetAssetDetailFailure, match="SESSION-1"):
            service.get_asset(command)

    def test_raises_failure_when_asset_not_in_device_result(
        self, service, mock_session_port, mock_engine, command
    ):
        """
        Dato un motore che non trova il risultato per lo specifico asset richiesto (Given),
        quando il servizio tenta la costruzione del DTO (When),
        allora deve sollevare una GetAssetDetailFailure (Then).
        """
        mock_session_port.get_evaluation_session.return_value = _make_mock_session()
        mock_device_result = MagicMock()
        mock_device_result.get_asset_result.return_value = None
        mock_engine.evaluate.return_value = mock_device_result

        with pytest.raises(GetAssetDetailFailure, match="ASSET-1"):
            service.get_asset(command)

    def test_raises_failure_when_asset_not_found_in_device(
        self, service, mock_session_port, mock_engine, command
    ):
        """
        Dato un identificativo asset che non appartiene al dispositivo in sessione (Given),
        quando il dominio segnala l'assenza (When),
        allora il servizio deve propagare il fallimento tramite GetAssetDetailFailure (Then).
        """
        mock_session = _make_mock_session()
        mock_session.device.get_asset.side_effect = AssetNotFoundError()
        mock_session_port.get_evaluation_session.return_value = mock_session
        mock_engine.evaluate.return_value = _make_mock_device_result()

        with pytest.raises(GetAssetDetailFailure, match="ASSET-1"):
            service.get_asset(command)