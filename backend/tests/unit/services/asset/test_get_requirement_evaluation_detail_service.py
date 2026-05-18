import pytest
from unittest.mock import MagicMock, patch

from core.domain.evaluation_engine.evaluation_detail import RequirementEvaluationDetail
from core.ports.inbound.asset.exceptions import GetRequirementEvaluationDetailFailure
from core.ports.inbound.asset.get_requirement_evaluation_detail_use_case import (
    GetRequirementEvaluationDetailCommand,
)
from core.ports.outbound.evaluation.exceptions import EvaluationSessionNotFoundError
from core.services.asset.get_requirement_evaluation_detail_service import (
    GetRequirementEvaluationDetailService,
)


@pytest.fixture
def mock_session_port():
    return MagicMock()


@pytest.fixture
def mock_engine():
    return MagicMock()


@pytest.fixture
def service(mock_session_port, mock_engine):
    return GetRequirementEvaluationDetailService(
        get_evaluation_session_port=mock_session_port,
        evaluation_engine=mock_engine,
    )


@pytest.fixture
def command():
    return GetRequirementEvaluationDetailCommand(
        session_id="SESSION-1",
        device_id="DEV-1",
        asset_id="ASSET-1",
        requirement_id="REQ-1",
    )


def _setup_happy_path(mock_session_port, mock_engine, command):
    mock_req = MagicMock()
    mock_req.requirement_id = command.requirement_id

    mock_device = MagicMock()
    mock_device.id = command.device_id

    mock_session = MagicMock()
    mock_session.device = mock_device
    mock_session.standard.get_requirement.return_value = mock_req
    mock_session_port.get_evaluation_session.return_value = mock_session

    mock_req_result = MagicMock()
    mock_req_result.requirement_id = command.requirement_id

    mock_asset_result = MagicMock()
    mock_asset_result.get_requirement_result.return_value = mock_req_result

    mock_device_result = MagicMock()
    mock_device_result.get_asset_result.return_value = mock_asset_result

    mock_engine.evaluate.return_value = mock_device_result

    return mock_session, mock_req_result, mock_req


class TestGetRequirementEvaluationDetailSuccess:
    @patch(
        "core.services.asset.get_requirement_evaluation_detail_service.EvaluationDetailBuilder"
    )
    def test_returns_result_from_builder(
        self, MockBuilder, service, mock_session_port, mock_engine, command
    ):
        """
        Dato un percorso di esecuzione senza errori (Given),
        quando viene richiesto il dettaglio valutativo di un requisito (When),
        allora il servizio deve restituire l'oggetto RequirementEvaluationDetail generato dal Builder (Then).
        """
        mock_session, mock_req_result, mock_req = _setup_happy_path(
            mock_session_port, mock_engine, command
        )

        mock_detail = MagicMock(spec=RequirementEvaluationDetail)
        MockBuilder.return_value.build_requirement_detail.return_value = mock_detail

        result = service.get_evaluation_detail(command)

        assert result is mock_detail

    @patch(
        "core.services.asset.get_requirement_evaluation_detail_service.EvaluationDetailBuilder"
    )
    def test_calls_builder_with_result_and_requirement(
        self, MockBuilder, service, mock_session_port, mock_engine, command
    ):
        """
        Dati il risultato della valutazione e l'entità del requisito recuperati (Given),
        quando il servizio prepara il dettaglio (When),
        allora deve delegare la costruzione al Builder passando correttamente sia il risultato grezzo che l'anagrafica del requisito (Then).
        """
        mock_session, mock_req_result, mock_req = _setup_happy_path(
            mock_session_port, mock_engine, command
        )

        service.get_evaluation_detail(command)

        MockBuilder.return_value.build_requirement_detail.assert_called_once_with(
            result=mock_req_result,
            req=mock_req,
        )

    def test_calls_engine_with_session_device_and_standard(
        self, service, mock_session_port, mock_engine, command
    ):
        """
        Data una sessione attiva recuperata (Given),
        quando viene richiesto il dettaglio del requisito (When),
        allora il servizio deve invocare il motore di valutazione passando il dispositivo e lo standard associati alla sessione (Then).
        """
        mock_session, _, _ = _setup_happy_path(mock_session_port, mock_engine, command)

        service.get_evaluation_detail(command)

        mock_engine.evaluate.assert_called_once_with(
            mock_session.device, mock_session.standard
        )

    def test_gets_requirement_from_standard(
        self, service, mock_session_port, mock_engine, command
    ):
        """
        Dato un identificativo di requisito (Given),
        quando il servizio deve ricostruire l'anagrafica del dettaglio (When),
        allora deve richiedere la definizione del requisito direttamente allo standard di conformità della sessione (Then).
        """
        mock_session, _, _ = _setup_happy_path(mock_session_port, mock_engine, command)

        service.get_evaluation_detail(command)

        mock_session.standard.get_requirement.assert_called_once_with("REQ-1")


class TestGetRequirementEvaluationDetailFailures:
    def test_raises_failure_when_session_not_found(
        self, service, mock_session_port, command
    ):
        """
        Dato un identificativo di sessione non valido (Given),
        quando viene richiesto il dettaglio del requisito (When),
        allora il servizio deve sollevare una GetRequirementEvaluationDetailFailure riportando l'ID sessione (Then).
        """
        mock_session_port.get_evaluation_session.side_effect = (
            EvaluationSessionNotFoundError()
        )

        with pytest.raises(GetRequirementEvaluationDetailFailure, match="SESSION-1"):
            service.get_evaluation_detail(command)

    def test_raises_failure_when_device_id_does_not_match(
        self, service, mock_session_port, mock_engine, command
    ):
        """
        Dato un comando per un dispositivo specifico (Given),
        quando l'identificativo del dispositivo in sessione è diverso da quello nel comando (When),
        allora deve essere sollevato un errore di fallimento del recupero dettagli (Then).
        """
        mock_device = MagicMock()
        mock_device.id = "WRONG-DEVICE"

        mock_session = MagicMock()
        mock_session.device = mock_device
        mock_session_port.get_evaluation_session.return_value = mock_session

        with pytest.raises(GetRequirementEvaluationDetailFailure, match="DEV-1"):
            service.get_evaluation_detail(command)

    def test_raises_failure_when_asset_result_is_none(
        self, service, mock_session_port, mock_engine, command
    ):
        """
        Dato un motore di valutazione che non produce risultati per l'asset richiesto (Given),
        quando il servizio tenta di estrarre il risultato del requisito (When),
        allora deve sollevare una GetRequirementEvaluationDetailFailure segnalando l'asset mancante (Then).
        """
        _setup_happy_path(mock_session_port, mock_engine, command)

        mock_device_result = MagicMock()
        mock_device_result.get_asset_result.return_value = None
        mock_engine.evaluate.return_value = mock_device_result

        with pytest.raises(GetRequirementEvaluationDetailFailure, match="ASSET-1"):
            service.get_evaluation_detail(command)

    def test_raises_failure_when_requirement_result_is_none(
        self, service, mock_session_port, mock_engine, command
    ):
        """
        Dato un asset rintracciato ma privo di risultato specifico per il requisito richiesto (Given),
        quando il servizio tenta di completare la richiesta (When),
        allora deve sollevare un'eccezione di fallimento riportando l'ID del requisito (Then).
        """
        _setup_happy_path(mock_session_port, mock_engine, command)

        mock_asset_result = MagicMock()
        mock_asset_result.get_requirement_result.return_value = None

        mock_device_result = MagicMock()
        mock_device_result.get_asset_result.return_value = mock_asset_result
        mock_engine.evaluate.return_value = mock_device_result

        with pytest.raises(GetRequirementEvaluationDetailFailure, match="REQ-1"):
            service.get_evaluation_detail(command)
