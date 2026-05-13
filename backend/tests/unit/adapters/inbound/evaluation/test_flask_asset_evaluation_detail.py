import pytest
from unittest.mock import MagicMock, patch
from flask import Flask, Blueprint

from pydantic import ValidationError

from core.domain.evaluation_engine.evaluation_result import EvaluationState
from core.domain.evaluation_object.asset import AssetType
from core.domain.evaluation_engine.evaluation_detail import AssetEvaluationDetail

from core.ports.inbound.asset.exceptions import GetAssetDetailFailure

from adapters.inbound.evaluation.evaluation_detail.flask_asset_evaluation_detail_controller import FlaskAssetEvaluationDetailController


def create_mock_validation_error() -> ValidationError:
    """Crea un finto ValidationError di Pydantic per testare il ramo 400."""
    return ValidationError.from_exception_data("GetAssetEvaluationDetailCommand", line_errors=[])

@pytest.fixture
def mock_use_case():
    return MagicMock()

@pytest.fixture
def app_and_client(mock_use_case):
    """Configura un'app Flask di test con il nostro controller registrato."""
    app = Flask(__name__)
    blueprint = Blueprint("test_asset_bp", __name__)
    
    controller = FlaskAssetEvaluationDetailController(mock_use_case)
    controller.register_routes(blueprint)
    
    app.register_blueprint(blueprint)
    
    with app.test_client() as client:
        yield client, mock_use_case


# --- TEST ----

class TestFlaskAssetEvaluationDetailController:

    @patch("adapters.inbound.evaluation.evaluation_detail.flask_asset_evaluation_detail_controller.render_template") 
    def test_ritorna_200_e_renderizza_dto_su_successo(self, mock_render_template, app_and_client):
        client, mock_use_case = app_and_client
        mock_render_template.return_value = "Mocked HTML"

        mock_asset_detail = MagicMock(spec=AssetEvaluationDetail)
        mock_asset_detail.name = "Server Database"
        mock_asset_detail.asset_type = getattr(AssetType, list(AssetType.__members__.keys())[0]) if hasattr(AssetType, '__members__') else "HARDWARE"
        mock_asset_detail.verdict = EvaluationState.PASS
        mock_asset_detail.description = "Database principale"
        
        mock_req = MagicMock()
        mock_req.requirement_id = "req-123"
        mock_req.state = EvaluationState.PASS
        mock_asset_detail.requirement_details = [mock_req]

        mock_use_case.get_asset.return_value = mock_asset_detail

        response = client.get("/sessions/s1/devices/d1/assets/a1")

        assert response.status_code == 200
        
        mock_use_case.get_asset.assert_called_once()
        command_chiamato = mock_use_case.get_asset.call_args[0][0]
        assert command_chiamato.session_id == "s1"
        assert command_chiamato.device_id == "d1"
        assert command_chiamato.asset_id == "a1"

        mock_render_template.assert_called_once()
        args, kwargs = mock_render_template.call_args
        assert args[0] == "layouts/asset_detail.html"
        
        dto_passato = kwargs["asset"]
        assert dto_passato["name"] == "Server Database"
        assert dto_passato["evaluation"] == EvaluationState.PASS
        assert len(dto_passato["requirements"]) == 1
        assert dto_passato["requirements"][0]["id"] == "req-123"

    @patch("adapters.inbound.evaluation.evaluation_detail.flask_asset_evaluation_detail_controller.render_template")
    @patch("adapters.inbound.evaluation.evaluation_detail.flask_asset_evaluation_detail_controller.GetAssetEvaluationDetailCommand")
    def test_ritorna_400_su_errore_di_validazione(self, mock_command_class, mock_render_template, app_and_client):
        client, _ = app_and_client
        mock_render_template.return_value = "Mocked 400 HTML"
        
        mock_command_class.side_effect = create_mock_validation_error()

        response = client.get("/sessions/s1/devices/d1/assets/a1")

        assert response.status_code == 400
        mock_render_template.assert_called_once()
        assert mock_render_template.call_args[0][0] == "errors/400.html"

    @patch("adapters.inbound.evaluation.evaluation_detail.flask_asset_evaluation_detail_controller.render_template") 
    def test_ritorna_404_su_fallimento_use_case(self, mock_render_template, app_and_client):
        client, mock_use_case = app_and_client
        mock_render_template.return_value = "Mocked 404 HTML"
        
        # Simula il fallimento del caso d'uso
        mock_use_case.get_asset.side_effect = GetAssetDetailFailure("Asset a1 non trovato")

        response = client.get("/sessions/s1/devices/d1/assets/a1")

        assert response.status_code == 404
        mock_render_template.assert_called_once()
        assert mock_render_template.call_args[0][0] == "errors/404.html"