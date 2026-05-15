import pytest
from unittest.mock import MagicMock, patch
from flask import Flask, Blueprint
from pydantic import ValidationError

from core.domain.evaluation_engine.evaluation_result import EvaluationState
from core.domain.evaluation_object.asset import AssetType
from core.domain.evaluation_engine.evaluation_detail import DeviceEvaluationDetail

from core.ports.inbound.evaluation.exceptions import GetEvaluationDetailFailure
from adapters.inbound.evaluation.evaluation_detail.flask_device_evaluation_detail_controller import FlaskDeviceEvaluationDetailController


def create_mock_validation_error() -> ValidationError:
    """Crea un finto ValidationError di Pydantic per testare il ramo 400."""
    return ValidationError.from_exception_data("GetDeviceEvaluationDetailCommand", line_errors=[])


@pytest.fixture
def mock_use_case():
    return MagicMock()

@pytest.fixture
def app_and_client(mock_use_case):
    """Configura un'app Flask di test con il nostro controller registrato."""
    app = Flask(__name__)
    blueprint = Blueprint("test_device_bp", __name__)
    
    controller = FlaskDeviceEvaluationDetailController(mock_use_case)
    controller.register_routes(blueprint)
    
    app.register_blueprint(blueprint)
    
    with app.test_client() as client:
        yield client, mock_use_case


# --- TESTS ---

class TestFlaskDeviceEvaluationDetailController:

    @patch("adapters.inbound.evaluation.evaluation_detail.flask_device_evaluation_detail_controller.render_template") 
    def test_ritorna_200_e_renderizza_dto_su_successo(self, mock_render_template, app_and_client):
        """
        Dati parametri di rotta validi (ID sessione e ID device) che permettono di recuperare la valutazione (Given),
        quando viene richiesta la dashboard di dettaglio del dispositivo (When),
        allora il controller deve mappare i risultati nel DTO e renderizzare il template della dashboard restituendo uno status code 200 OK (Then).
        """
        client, mock_use_case = app_and_client
        mock_render_template.return_value = "Mocked HTML"

        # Crea un Mock puro per il dominio del Device
        mock_device_detail = MagicMock(spec=DeviceEvaluationDetail)
        mock_device_detail.name = "Router Principale"
        mock_device_detail.operating_system = "Cisco IOS"
        mock_device_detail.description = "Router di core della rete aziendale"
        mock_device_detail.verdict = EvaluationState.PASS
        
        # Simula un asset valutato all'interno del device
        mock_asset = MagicMock()
        mock_asset.asset_id = "asset-999"
        mock_asset.name = "Interfaccia WAN"
        mock_asset.asset_type = AssetType.NETWORK
        mock_asset.verdict = EvaluationState.PASS
        
        mock_device_detail.asset_details = [mock_asset]

        mock_use_case.get_device_evaluation_detail.return_value = mock_device_detail

        response = client.get("/dashboard/sessions/s1/devices/d1")

        assert response.status_code == 200
        
        mock_use_case.get_device_evaluation_detail.assert_called_once()
        command_chiamato = mock_use_case.get_device_evaluation_detail.call_args[0][0]
        assert command_chiamato.session_id == "s1"
        assert command_chiamato.device_id == "d1"

        # Verifichiamo il render_template e il mapping del DTO
        mock_render_template.assert_called_once()
        args, kwargs = mock_render_template.call_args
        assert args[0] == "layouts/dashboard/dashboard.html"
        
        dto_passato = kwargs["device_detail"]
        
        assert dto_passato["device_name"] == "Router Principale"
        assert dto_passato["device_os"] == "Cisco IOS"
        assert dto_passato["device_evaluation_result"] == EvaluationState.PASS
        assert len(dto_passato["asset_list"]) == 1
        assert dto_passato["asset_list"][0]["asset_id"] == "asset-999"
        assert dto_passato["asset_list"][0]["asset_name"] == "Interfaccia WAN"

    @patch("adapters.inbound.evaluation.evaluation_detail.flask_device_evaluation_detail_controller.render_template")
    @patch("adapters.inbound.evaluation.evaluation_detail.flask_device_evaluation_detail_controller.GetDeviceEvaluationDetailCommand")
    def test_ritorna_400_su_errore_di_validazione(self, mock_command_class, mock_render_template, app_and_client):
        """
        Dati dei parametri mancanti o malformati che generano un errore di validazione durante la creazione del Command (Given),
        quando il controller riceve la richiesta per la dashboard del dispositivo (When),
        allora l'eccezione deve essere gestita renderizzando la pagina di errore associata allo status 400 Bad Request (Then).
        """
        client, _ = app_and_client
        mock_render_template.return_value = "Mocked 400 HTML"
        
        mock_command_class.side_effect = create_mock_validation_error()

        response = client.get("/dashboard/sessions/s1/devices/d1")

        assert response.status_code == 400
        mock_render_template.assert_called_once()
        assert mock_render_template.call_args[0][0] == "errors/400.html"

    @patch("adapters.inbound.evaluation.evaluation_detail.flask_device_evaluation_detail_controller.render_template") 
    def test_ritorna_404_su_fallimento_use_case(self, mock_render_template, app_and_client):
        """
        Dato uno scenario in cui i dettagli valutativi non sono reperibili e lo use case solleva una GetEvaluationDetailFailure (Given),
        quando l'utente tenta di visualizzare il dispositivo (When),
        allora il controller deve catturare l'eccezione e restituire il template di errore con status code 404 Not Found (Then).
        """
        client, mock_use_case = app_and_client
        mock_render_template.return_value = "Mocked 404 HTML"
        
        mock_use_case.get_device_evaluation_detail.side_effect = GetEvaluationDetailFailure("Dispositivo d1 non trovato")

        response = client.get("/dashboard/sessions/s1/devices/d1")

        assert response.status_code == 404
        mock_render_template.assert_called_once()
        assert mock_render_template.call_args[0][0] == "errors/404.html"