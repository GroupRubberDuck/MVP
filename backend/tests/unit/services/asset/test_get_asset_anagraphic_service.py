import pytest
from unittest.mock import MagicMock

from core.domain.evaluation_object.asset.asset_anagraphic import AssetAnagraphic
from core.domain.evaluation_object.exceptions import AssetNotFoundError
from core.ports.inbound.asset.exceptions import GetAssetAnagraphicFailure
from core.ports.inbound.asset.get_asset_anagraphic_use_case import (
    GetAssetAnagraphicCommand,
)
from core.ports.outbound.evaluation.exceptions import EvaluationSessionNotFoundError
from core.services.asset.get_asset_anagraphic_service import GetAssetAnagraphicService


@pytest.fixture
def mock_session_port():
    return MagicMock()


@pytest.fixture
def service(mock_session_port):
    return GetAssetAnagraphicService(get_evaluation_session_port=mock_session_port)


@pytest.fixture
def command():
    return GetAssetAnagraphicCommand(
        device_id="DEVICE-123", session_id="SESSION-123", asset_id="ASSET-456"
    )


def _make_mock_session(asset_id: str, anagraphic_obj: MagicMock) -> MagicMock:
    """Helper per costruire un mock della sessione con device e asset annidati."""
    mock_asset = MagicMock()
    mock_asset.id = asset_id
    mock_asset.anagraphic = anagraphic_obj

    mock_session = MagicMock()
    mock_session.device.get_asset.return_value = mock_asset
    return mock_session


class TestGetAssetAnagraphicSuccess:
    def test_returns_correct_anagraphic_object(
        self, service, mock_session_port, command
    ):
        """
        Dato un Asset esistente all'interno di una sessione attiva (Given),
        quando viene richiesto il recupero dei suoi dati anagrafici (When),
        allora il servizio deve restituire l'oggetto AssetAnagraphic corrispondente recuperato dal dominio (Then).
        """
        mock_anagraphic = MagicMock(spec=AssetAnagraphic)
        mock_session_port.get_evaluation_session.return_value = _make_mock_session(
            command.asset_id, mock_anagraphic
        )

        result = service.get_asset_anagraphic(command)
        assert result == mock_anagraphic

    def test_calls_port_with_correct_session_id(
        self, service, mock_session_port, command
    ):
        """
        Dato un comando di recupero anagrafica contenente un ID sessione (Given),
        quando il servizio viene eseguito (When),
        allora deve interrogare la porta di uscita della sessione utilizzando l'identificativo corretto (Then).
        """
        mock_session_port.get_evaluation_session.return_value = _make_mock_session(
            command.asset_id, MagicMock()
        )

        service.get_asset_anagraphic(command)
        mock_session_port.get_evaluation_session.assert_called_once_with("SESSION-123")

    def test_calls_device_with_correct_asset_id(
        self, service, mock_session_port, command
    ):
        """
        Dato un ID asset fornito nel comando (Given),
        quando la sessione viene recuperata con successo (When),
        allora il servizio deve richiedere al dispositivo l'asset specifico utilizzando l'ID fornito (Then).
        """
        mock_session = _make_mock_session(command.asset_id, MagicMock())
        mock_session_port.get_evaluation_session.return_value = mock_session

        service.get_asset_anagraphic(command)

        mock_session.device.get_asset.assert_called_once_with("ASSET-456")


class TestGetAssetAnagraphicFailures:
    def test_raises_failure_when_session_not_found(
        self, service, mock_session_port, command
    ):
        """
        Dato un ID sessione non presente nel sistema (Given),
        quando si tenta di recuperare l'anagrafica di un asset (When),
        allora il servizio deve intercettare l'errore di sessione mancante e sollevare una GetAssetAnagraphicFailure (Then).
        """
        mock_session_port.get_evaluation_session.side_effect = (
            EvaluationSessionNotFoundError()
        )

        with pytest.raises(GetAssetAnagraphicFailure, match="SESSION-123"):
            service.get_asset_anagraphic(command)

    def test_raises_failure_when_asset_not_found_in_device(
        self, service, mock_session_port, command
    ):
        """
        Data una sessione valida ma un dispositivo che non contiene l'ID asset richiesto (Given),
        quando il dominio solleva un AssetNotFoundError (When),
        allora il servizio deve propagare il fallimento tramite l'eccezione GetAssetAnagraphicFailure riportando l'ID dell'asset (Then).
        """
        mock_session = MagicMock()
        mock_session.device.get_asset.side_effect = AssetNotFoundError()
        mock_session_port.get_evaluation_session.return_value = mock_session

        with pytest.raises(GetAssetAnagraphicFailure, match="ASSET-456"):
            service.get_asset_anagraphic(command)
