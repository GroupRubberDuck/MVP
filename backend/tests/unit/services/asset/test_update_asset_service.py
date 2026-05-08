import pytest
from unittest.mock import MagicMock

from core.ports.inbound.asset.exceptions import UpdateAssetFailure
from core.ports.inbound.asset.update_asset_use_case import UpdateAssetCommand
from core.ports.outbound.evaluation.exceptions import EvaluationSessionNotFoundError
from core.domain.evaluation_object.exceptions import AssetNotFoundError
from core.services.asset.update_asset_service import UpdateAssetService
from core.domain.evaluation_object.asset import AssetType


# --- FIXTURES ---

@pytest.fixture
def mock_get_evaluation_session_port():
    return MagicMock()

@pytest.fixture
def mock_save_evaluation_session_port():
    return MagicMock()

@pytest.fixture
def service(mock_get_evaluation_session_port, mock_save_evaluation_session_port):
    return UpdateAssetService(
        get_evaluation_session_port=mock_get_evaluation_session_port,
        save_evaluation_session_port=mock_save_evaluation_session_port,
    )

@pytest.fixture
def command():

    return UpdateAssetCommand(
        session_id="SESSION-123",
        device_id="device-1",
        asset_id="ASSET-456",
        name="Nuovo Nome Asset",
        asset_type=AssetType.NETWORK,
        description="Nuova descrizione"
    )

def _make_mock_session(command: UpdateAssetCommand, mock_updated_asset: MagicMock) -> MagicMock:

    mock_asset = MagicMock()
    mock_asset.update_anagraphic.return_value = mock_updated_asset

    mock_device = MagicMock()
    mock_device.get_asset.return_value = mock_asset

    mock_session = MagicMock()
    mock_session.device = mock_device
    
    return mock_session


class TestUpdateAssetSuccess:

    def test_updates_asset_and_saves_session_successfully(
        self, service, mock_get_evaluation_session_port, mock_save_evaluation_session_port, command
    ):
        mock_updated_asset = MagicMock()
        mock_session = _make_mock_session(command, mock_updated_asset)
        mock_get_evaluation_session_port.get_evaluation_session.return_value = mock_session

        service.update_asset(command)

        mock_session.device.get_asset.assert_called_once_with("ASSET-456")
        
        mock_asset = mock_session.device.get_asset.return_value
        mock_asset.update_anagraphic.assert_called_once_with(
            name="Nuovo Nome Asset",
            asset_type=AssetType.NETWORK,
            description="Nuova descrizione"
        )

        mock_save_evaluation_session_port.save_evaluation_session.assert_called_once_with(mock_session)


class TestUpdateAssetFailures:

    def test_raises_failure_when_session_not_found(
        self, service, mock_get_evaluation_session_port, command
    ):
        mock_get_evaluation_session_port.get_evaluation_session.side_effect = EvaluationSessionNotFoundError()

        with pytest.raises(UpdateAssetFailure, match="SESSION-123"):
            service.update_asset(command)

    def test_raises_failure_when_asset_not_found(
        self, service, mock_get_evaluation_session_port, command
    ):
        mock_session = MagicMock()
        mock_session.device.get_asset.side_effect = AssetNotFoundError()
        mock_get_evaluation_session_port.get_evaluation_session.return_value = mock_session

        with pytest.raises(UpdateAssetFailure, match="ASSET-456"):
            service.update_asset(command)

    def test_raises_failure_on_invalid_data_value_error(
        self, service, mock_get_evaluation_session_port, command
    ):
        mock_asset = MagicMock()
        mock_asset.update_anagraphic.side_effect = ValueError("Il nome non può essere vuoto")
        
        mock_session = MagicMock()
        mock_session.device.get_asset.return_value = mock_asset
        mock_get_evaluation_session_port.get_evaluation_session.return_value = mock_session

        with pytest.raises(UpdateAssetFailure, match="Il nome non può essere vuoto"):
            service.update_asset(command)