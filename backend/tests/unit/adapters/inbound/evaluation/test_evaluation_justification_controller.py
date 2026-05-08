import json
import pytest
from unittest.mock import MagicMock
from flask import Flask
 
from adapters.inbound.evaluation.evaluation_justification_controller import (
    EvaluationJustificationController,
    evaluation_justification_blueprint,
)
from core.services.evaluation.insert_justification_command import InsertJustificationCommand
 
 
BASE_URL = "/sessions/session-1/assets/asset-1/requirements/REQ-1/nodes/NODE-1/justification"
 
 
@pytest.fixture
def app():
    mock_use_case = MagicMock()
    EvaluationJustificationController(mock_use_case)
    flask_app = Flask(__name__)
    flask_app.register_blueprint(evaluation_justification_blueprint)
    flask_app.config["TESTING"] = True
    return flask_app, mock_use_case
 
 
class TestEvaluationJustificationController:
 
    def test_risponde_200_con_payload_corretto(self, app):
        flask_app, _ = app
        with flask_app.test_client() as client:
            response = client.put(BASE_URL, json={"justification": "testo"})
 
        assert response.status_code == 200
 
    def test_chiama_use_case_una_volta(self, app):
        flask_app, mock_use_case = app
        with flask_app.test_client() as client:
            client.put(BASE_URL, json={"justification": "testo"})
 
        mock_use_case.insert_justification.assert_called_once()
 
    def test_command_ha_i_campi_corretti(self, app):
        flask_app, mock_use_case = app
        with flask_app.test_client() as client:
            client.put(BASE_URL, json={"justification": "testo giustificazione"})
 
        command: InsertJustificationCommand = mock_use_case.insert_justification.call_args[0][0]
        assert command.session_id == "session-1"
        assert command.asset_id == "asset-1"
        assert command.requirement_id == "REQ-1"
        assert command.node_id == "NODE-1"
        assert command.justification == "testo giustificazione"
 
    def test_body_senza_justification_usa_stringa_vuota(self, app):
        flask_app, mock_use_case = app
        with flask_app.test_client() as client:
            client.put(BASE_URL, json={})
 
        command: InsertJustificationCommand = mock_use_case.insert_justification.call_args[0][0]
        assert command.justification == ""
 
    def test_risposta_contiene_messaggio(self, app):
        flask_app, _ = app
        with flask_app.test_client() as client:
            response = client.put(BASE_URL, json={"justification": "testo"})
 
        body = json.loads(response.data)
        assert "message" in body
 