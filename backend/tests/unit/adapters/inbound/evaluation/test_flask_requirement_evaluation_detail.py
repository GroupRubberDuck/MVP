import pytest
from unittest.mock import MagicMock, patch
from flask import Flask, Blueprint

from pydantic import ValidationError

from core.domain.evaluation_engine.evaluation_result import EvaluationState
from core.domain.evaluation_standard.standard_verdict import StandardVerdict
from core.domain.evaluation_engine.evaluation_detail import (
    RequirementEvaluationDetail,
    NodeDetail
)
from core.ports.inbound.asset.exceptions import GetRequirementEvaluationDetailFailure
from adapters.inbound.evaluation.evaluation_detail.flask_requirement_evaluation_detail_controller import FlaskRequirementEvaluationDetailController

def create_mock_validation_error() -> ValidationError:
    """Crea un finto ValidationError di Pydantic per testare il ramo 400."""
    return ValidationError.from_exception_data("GetRequirementEvaluationDetailCommand", line_errors=[])

@pytest.fixture
def mock_use_case():
    return MagicMock()

@pytest.fixture
def app_and_client(mock_use_case):
    """Configura un'app Flask di test con il nostro controller registrato."""
    app = Flask(__name__)
    blueprint = Blueprint("test_bp", __name__)
    
    controller = FlaskRequirementEvaluationDetailController(mock_use_case)
    controller.register_routes(blueprint)
    
    app.register_blueprint(blueprint)
    
    with app.test_client() as client:
        yield client, mock_use_case


# --- TESTS ---

class TestFlaskRequirementEvaluationDetail:

    @patch("adapters.inbound.evaluation.evaluation_detail.flask_requirement_evaluation_detail_controller.render_template")
    def test_ritorna_200_e_renderizza_dto_su_successo(self, mock_render_template, app_and_client):
        """
        Dati i parametri di rotta validi per recuperare i dettagli di valutazione di un requisito (Given),
        quando l'utente richiede la vista di dettaglio (When),
        allora il controller deve mappare i dati (incluso l'albero decisionale e i nodi) nel DTO, renderizzare il template corretto e restituire uno status code 200 OK (Then).
        """
        client, mock_use_case = app_and_client
        mock_render_template.return_value = "Mocked HTML"

        decision_node = NodeDetail(
            node_id="n1",
            node_type="decision",
            parent_id=None,
            question="Is it secure?",
            child_on_true_id="n2",
            child_on_false_id="n3",
            verdict=None
        )
        leaf_node = NodeDetail(
            node_id="n2",
            node_type="leaf",
            parent_id="n1",
            question=None,
            child_on_true_id=None,
            child_on_false_id=None,
            verdict=StandardVerdict.PASS
        )
        
        mock_detail = RequirementEvaluationDetail(
            requirement_id="r1",
            justification="Test justification",
            name="Req-1",
            description="Norm description",
            target="Target desc",
            state=EvaluationState.PASS,
            dependencies=(("dep-1", EvaluationState.PASS),),
            node_choices={"n1": True},
            root_id="n1",
            nodes={"n1": decision_node, "n2": leaf_node}
        )
        mock_use_case.get_evaluation_detail.return_value = mock_detail

        response = client.get("/sessions/s1/devices/d1/assets/a1/requirements/r1")

        assert response.status_code == 200
        
        mock_use_case.get_evaluation_detail.assert_called_once()
        command_chiamato = mock_use_case.get_evaluation_detail.call_args[0][0]
        assert command_chiamato.session_id == "s1"
        assert command_chiamato.requirement_id == "r1"

        mock_render_template.assert_called_once()
        args, kwargs = mock_render_template.call_args
        assert args[0] == "layouts/requirement_detail.html"
        
        dto_passato = kwargs["requirement"]
        dto_passato = kwargs["requirement"]
        assert dto_passato["name"] == "Req-1"
        assert dto_passato["decision_tree"]["root_node_id"] == "n1"
        assert len(dto_passato["decision_tree"]["nodes"]) == 2
        assert dto_passato["decision_tree"]["nodes"]["n1"]["node_type"] == "decision"
        assert dto_passato["decision_tree"]["nodes"]["n2"]["node_type"] == "leaf"

    @patch("adapters.inbound.evaluation.evaluation_detail.flask_requirement_evaluation_detail_controller.render_template")
    @patch("adapters.inbound.evaluation.evaluation_detail.flask_requirement_evaluation_detail_controller.GetRequirementEvaluationDetailCommand")
    def test_ritorna_400_su_errore_di_validazione(self, mock_command_class, mock_render_template, app_and_client):
        """
        Dati dei parametri di input malformati o mancanti che causano un errore di validazione nella creazione del Command (Given),
        quando il controller elabora la richiesta (When),
        allora l'eccezione deve essere gestita restituendo la pagina di errore associata allo status 400 Bad Request (Then).
        """
        client, _ = app_and_client
        mock_render_template.return_value = "Mocked 400 HTML"
        
        mock_command_class.side_effect = create_mock_validation_error()

        response = client.get("/sessions/s1/devices/d1/assets/a1/requirements/r1")

        assert response.status_code == 400
        mock_render_template.assert_called_once()
        assert mock_render_template.call_args[0][0] == "errors/400.html"

    @patch("adapters.inbound.evaluation.evaluation_detail.flask_requirement_evaluation_detail_controller.render_template")
    def test_ritorna_404_su_fallimento_use_case(self, mock_render_template, app_and_client):
        """
        Dato uno scenario in cui i dettagli del requisito non sono reperibili e lo use case solleva una GetRequirementEvaluationDetailFailure (Given),
        quando l'utente tenta di accedere alla risorsa (When),
        allora il controller deve intercettare l'errore e renderizzare il template di errore 404 Not Found (Then).
        """
        client, mock_use_case = app_and_client
        mock_render_template.return_value = "Mocked 404 HTML"
        
        mock_use_case.get_evaluation_detail.side_effect = GetRequirementEvaluationDetailFailure("Non trovato")

        response = client.get("/sessions/s1/devices/d1/assets/a1/requirements/r1")
        
        assert response.status_code == 404
        mock_render_template.assert_called_once()
        assert mock_render_template.call_args[0][0] == "errors/404.html"