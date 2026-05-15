import pytest
from unittest.mock import MagicMock

from core.ports.inbound.asset.exceptions import DeleteAssetFailure
from core.ports.inbound.asset.delete_asset_use_case import DeleteAssetCommand
from core.ports.outbound.evaluation.exceptions import EvaluationSessionNotFoundError
from core.domain.evaluation_object.exceptions import AssetNotFoundError
from core.services.asset.delete_asset_service import DeleteAssetService


# --- FIXTURES ---

@pytest.fixture
def mock_get_evaluation_session_port():
    return MagicMock()

@pytest.fixture
def mock_save_evaluation_session_port():
    return MagicMock()

@pytest.fixture
def service(mock_get_evaluation_session_port, mock_save_evaluation_session_port):
    return DeleteAssetService(
        get_evaluation_session_port=mock_get_evaluation_session_port,
        save_evaluation_session_port=mock_save_evaluation_session_port,
    )

@pytest.fixture
def command():
    return DeleteAssetCommand(
        session_id="SESSION-123",
        device_id="DEV-001",
        asset_id="ASSET-456"
    )

def _make_mock_session() -> MagicMock:
    mock_device = MagicMock()
    mock_session = MagicMock()
    mock_session.device = mock_device
    return mock_session



class TestDeleteAssetSuccess:

    def test_deletes_asset_and_saves_session_successfully(
        self, service, mock_get_evaluation_session_port, mock_save_evaluation_session_port, command
    ):
        """
        Dato un identificativo di sessione e un identificativo asset validi (Given),
        quando viene richiesto al servizio di eliminare l'asset (When),
        allora il servizio deve rimuovere l'asset dal dispositivo e salvare lo stato aggiornato della sessione (Then).
        """
        mock_session = _make_mock_session()
        mock_get_evaluation_session_port.get_evaluation_session.return_value = mock_session

        service.delete_asset(command)

        mock_get_evaluation_session_port.get_evaluation_session.assert_called_once_with("SESSION-123")
        
        mock_session.device.remove_asset.assert_called_once_with("ASSET-456")

        mock_save_evaluation_session_port.save_evaluation_session.assert_called_once_with(mock_session)


class TestDeleteAssetFailures:

    def test_raises_failure_when_session_not_found(
        self, service, mock_get_evaluation_session_port, command
    ):
        """
        Dato un ID sessione inesistente o non caricato (Given),
        quando viene tentata la cancellazione di un asset (When),
        allora il servizio deve intercettare l'errore di sessione mancante e sollevare una DeleteAssetFailure specifica (Then).
        """
        mock_get_evaluation_session_port.get_evaluation_session.side_effect = EvaluationSessionNotFoundError()

        with pytest.raises(DeleteAssetFailure, match="SESSION-123"):
            service.delete_asset(command)

    def test_raises_failure_when_asset_not_found(
        self, service, mock_get_evaluation_session_port, command
    ):
        """
        Data una sessione valida ma un ID asset non associato al dispositivo (Given),
        quando il dominio solleva un errore di asset non trovato (When),
        allora il servizio deve propagare il fallimento tramite l'eccezione DeleteAssetFailure riportando l'ID dell'asset (Then).
        """

        mock_session = _make_mock_session()

        mock_session.device.remove_asset.side_effect = AssetNotFoundError()
        mock_get_evaluation_session_port.get_evaluation_session.return_value = mock_session

        with pytest.raises(DeleteAssetFailure, match="ASSET-456"):
            service.delete_asset(command)