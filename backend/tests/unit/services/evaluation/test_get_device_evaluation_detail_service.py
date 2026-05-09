import pytest
from unittest.mock import MagicMock

from core.services.evaluation.get_device_evaluation_detail_service import GetDeviceEvaluationDetailService
from core.ports.inbound.evaluation.get_device_evaluation_detail_use_case import GetDeviceEvaluationDetailCommand
from core.ports.inbound.evaluation.exceptions import GetEvaluationDetailFailure
from core.ports.outbound.evaluation.exceptions import EvaluationSessionNotFoundError
from core.domain.evaluation_object.asset.asset_type import AssetType


def make_command(session_id="session-123") -> GetDeviceEvaluationDetailCommand:
    return GetDeviceEvaluationDetailCommand(session_id=session_id)

def make_service():
    mock_get_session_port = MagicMock()
    mock_engine = MagicMock()
    
    service = GetDeviceEvaluationDetailService(
        get_evaluation_session_port=mock_get_session_port,
        evaluation_engine=mock_engine
    )
    
    return service, mock_get_session_port, mock_engine


# --- TEST SUITE ---

class TestGetDeviceEvaluationDetailService:

    def test_solleva_failure_se_sessione_non_trovata(self):
        service, mock_get_session, _ = make_service()
        mock_get_session.get_evaluation_session.side_effect = EvaluationSessionNotFoundError("Non trovata")

        with pytest.raises(GetEvaluationDetailFailure) as exc_info:
            service.get_device_evaluation_detail(make_command(session_id="fake-session"))

        assert "Sessione 'fake-session' non trovata" in str(exc_info.value)

    def test_get_detail_mappa_correttamente_i_dati_di_successo(self):
        service, mock_get_session, mock_engine = make_service()
        command = make_command()

        # Prepariamo il mock del Dominio (Sessione, Device, Standard)
        mock_session = MagicMock()
        mock_device = MagicMock()
        mock_standard = MagicMock()
        
        mock_session.device = mock_device
        mock_session.standard = mock_standard
        mock_get_session.get_evaluation_session.return_value = mock_session

        # Anagrafica Device
        mock_device.id = "dev-1"
        mock_device.name = "Device Test"
        mock_device.os = "Linux"
        mock_device.description = "Desc"
        mock_device.standard_id = "std-1"

        # Anagrafica Asset (restituito dal mock_device)
        mock_asset = MagicMock()
        mock_asset.id = "asset-1"
        mock_asset.anagraphic.name = "Asset Name"
        mock_asset.anagraphic.asset_type = AssetType.NETWORK
        mock_asset.anagraphic.description = "Asset Desc"
        mock_device.get_asset.return_value = mock_asset

        # Anagrafica Requirement (restituito dal mock_standard)
        mock_req = MagicMock()
        mock_req.name = "Req Name"
        mock_req.description = "Req Desc"
        mock_req.target_description = "Target Desc"
        mock_req.decision_tree.nodes = {"node-1": MagicMock()} 
        mock_standard.get_requirement.return_value = mock_req

        # Prepariamo il mock del Risultato dell'Engine
        mock_device_result = MagicMock()
        mock_asset_result = MagicMock()
        mock_req_result = MagicMock()

        # Engine -> restituisce device_result
        mock_engine.evaluate.return_value = mock_device_result
        mock_device_result.verdict = "PASS"
        mock_device_result.asset_results = [mock_asset_result]

        # DeviceResult -> contiene asset_result
        mock_asset_result.asset_id = "asset-1"
        mock_asset_result.verdict = "PASS"
        mock_asset_result.requirement_results = [mock_req_result]

        # AssetResult -> contiene req_result
        mock_req_result.requirement_id = "req-1"
        mock_req_result.justification = "Giustificato"
        mock_req_result.node_choices = {"node-1": True}
        mock_req_result.state = "PASS"
        mock_req_result.dependencies = (("dep-1", "PASS"),)

        result = service.get_device_evaluation_detail(command)

        # Verifichiamo che l'orchestrazione sia avvenuta
        mock_get_session.get_evaluation_session.assert_called_once_with("session-123")
        mock_engine.evaluate.assert_called_once_with(mock_device, mock_standard)

        # Verifichiamo il mapping del Device
        assert result.device_id == "dev-1"
        assert result.name == "Device Test"
        assert result.operating_system == "Linux"
        assert result.verdict == "PASS"
        assert len(result.asset_details) == 1

        # Verifichiamo il mapping dell'Asset
        asset_detail = result.asset_details[0]
        assert asset_detail.asset_id == "asset-1"
        assert asset_detail.name == "Asset Name"
        assert asset_detail.asset_type == "network"
        assert asset_detail.verdict == "PASS"
        assert len(asset_detail.requirement_details) == 1

        # Verifichiamo il mapping del Requirement
        req_detail = asset_detail.requirement_details[0]
        assert req_detail.requirement_id == "req-1"
        assert req_detail.name == "Req Name"
        assert req_detail.target == "Target Desc"
        assert req_detail.justification == "Giustificato"
        assert req_detail.node_choices == {"node-1": True}
        assert req_detail.state == "PASS"
        assert req_detail.dependencies == (("dep-1", "PASS"),)