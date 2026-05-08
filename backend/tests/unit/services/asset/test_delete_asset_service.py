import pytest
from unittest.mock import MagicMock

from core.ports.inbound.asset.exceptions import DeleteAssetFailure
from core.ports.inbound.asset.delete_asset_use_case import DeleteAssetCommand
from core.ports.outbound.evaluation.exceptions import SessionNotFoundError
from core.domain.evaluation_object.exceptions import AssetNotFoundError
from core.services.asset.delete_asset_service import DeleteAssetService


# --- FIXTURES ---

@pytest.fixture
def mock_get_session_port():
    return MagicMock()

@pytest.fixture
def mock_save_session_port():
    return MagicMock()

@pytest.fixture
def service(mock_get_session_port, mock_save_session_port):
    return DeleteAssetService(
        get_session_port=mock_get_session_port,
        save_session_port=mock_save_session_port,
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
        self, service, mock_get_session_port, mock_save_session_port, command
    ):
        mock_session = _make_mock_session()
        mock_get_session_port.get_session.return_value = mock_session

        service.delete_asset(command)

        mock_get_session_port.get_session.assert_called_once_with("SESSION-123")
        
        mock_session.device.remove_asset.assert_called_once_with("ASSET-456")

        mock_save_session_port.save_session.assert_called_once_with(mock_session)


class TestDeleteAssetFailures:

    def test_raises_failure_when_session_not_found(
        self, service, mock_get_session_port, command
    ):
        mock_get_session_port.get_session.side_effect = SessionNotFoundError()

        with pytest.raises(DeleteAssetFailure, match="SESSION-123"):
            service.delete_asset(command)

    def test_raises_failure_when_asset_not_found(
        self, service, mock_get_session_port, command
    ):

        mock_session = _make_mock_session()

        mock_session.device.remove_asset.side_effect = AssetNotFoundError()
        mock_get_session_port.get_session.return_value = mock_session

        with pytest.raises(DeleteAssetFailure, match="ASSET-456"):
            service.delete_asset(command)