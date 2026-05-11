import pytest
from unittest.mock import MagicMock

from core.domain.evaluation_standard.evaluation_state import EvaluationState
from core.domain.evaluation_object.exceptions import AssetNotFoundError
from core.ports.inbound.asset.exceptions import GetAssetDetailFailure
from core.ports.inbound.asset.get_asset_evaluation_detail_use_case import GetAssetDetailCommand
from core.ports.outbound.evaluation.exceptions import EvaluationSessionNotFoundError
from core.services.asset.get_asset_detail_service import GetAssetDetailService


@pytest.fixture
def mock_session_port():
    return MagicMock()


@pytest.fixture
def mock_engine():
    return MagicMock()


@pytest.fixture
def service(mock_session_port, mock_engine):
    return GetAssetDetailService(
        get_evaluation_session_port=mock_session_port,
        evaluation_engine=mock_engine,
    )


@pytest.fixture
def command():
    return GetAssetDetailCommand(device_id="DEVICE-1", asset_id="ASSET-1", session_id="SESSION-1")


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
        mock_session_port.get_evaluation_session.return_value = _make_mock_session()
        mock_engine.evaluate.return_value = _make_mock_device_result()

        result = service.get_asset(command)

        assert result.asset_id == "ASSET-1"

    def test_returns_asset_detail_with_correct_name(
        self, service, mock_session_port, mock_engine, command
    ):
        mock_session_port.get_evaluation_session.return_value = _make_mock_session()
        mock_engine.evaluate.return_value = _make_mock_device_result()

        result = service.get_asset(command)

        assert result.name == "Network Interface"

    def test_returns_asset_detail_with_pass_verdict(
        self, service, mock_session_port, mock_engine, command
    ):
        mock_session_port.get_evaluation_session.return_value = _make_mock_session()
        mock_engine.evaluate.return_value = _make_mock_device_result(verdict=EvaluationState.PASS)

        result = service.get_asset(command)

        assert result.verdict == EvaluationState.PASS

    def test_returns_asset_detail_with_fail_verdict(
        self, service, mock_session_port, mock_engine, command
    ):
        mock_session_port.get_evaluation_session.return_value = _make_mock_session()
        mock_engine.evaluate.return_value = _make_mock_device_result(verdict=EvaluationState.FAIL)

        result = service.get_asset(command)

        assert result.verdict == EvaluationState.FAIL

    def test_returns_empty_requirement_details_when_no_requirements(
        self, service, mock_session_port, mock_engine, command
    ):
        mock_session_port.get_evaluation_session.return_value = _make_mock_session()
        mock_engine.evaluate.return_value = _make_mock_device_result(requirement_results=())

        result = service.get_asset(command)

        assert result.requirement_details == ()

    def test_calls_port_with_correct_session_id(
        self, service, mock_session_port, mock_engine, command
    ):
        mock_session_port.get_evaluation_session.return_value = _make_mock_session()
        mock_engine.evaluate.return_value = _make_mock_device_result()

        service.get_asset(command)

        mock_session_port.get_evaluation_session.assert_called_once_with("SESSION-1")

    def test_calls_engine_with_session_device_and_standard(
        self, service, mock_session_port, mock_engine, command
    ):
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
        mock_session_port.get_evaluation_session.return_value = _make_mock_session()
        mock_device_result = _make_mock_device_result()
        mock_engine.evaluate.return_value = mock_device_result

        service.get_asset(command)

        mock_device_result.get_asset_result.assert_called_once_with("ASSET-1")


class TestGetAssetDetailFailures:

    def test_raises_failure_when_session_not_found(
        self, service, mock_session_port, command
    ):
        mock_session_port.get_evaluation_session.side_effect = EvaluationSessionNotFoundError()

        with pytest.raises(GetAssetDetailFailure, match="SESSION-1"):
            service.get_asset(command)

    def test_raises_failure_when_asset_not_in_device_result(
        self, service, mock_session_port, mock_engine, command
    ):
        mock_session_port.get_evaluation_session.return_value = _make_mock_session()
        mock_device_result = MagicMock()
        mock_device_result.get_asset_result.return_value = None
        mock_engine.evaluate.return_value = mock_device_result

        with pytest.raises(GetAssetDetailFailure, match="ASSET-1"):
            service.get_asset(command)

    def test_raises_failure_when_asset_not_found_in_device(
        self, service, mock_session_port, mock_engine, command
    ):
        mock_session = _make_mock_session()
        mock_session.device.get_asset.side_effect = AssetNotFoundError()
        mock_session_port.get_evaluation_session.return_value = mock_session
        mock_engine.evaluate.return_value = _make_mock_device_result()

        with pytest.raises(GetAssetDetailFailure, match="ASSET-1"):
            service.get_asset(command)