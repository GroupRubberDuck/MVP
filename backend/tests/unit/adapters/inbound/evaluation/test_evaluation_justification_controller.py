import json
import pytest
from unittest.mock import MagicMock
from flask import Flask, blueprints
 
from adapters.inbound.evaluation.flask_insert_justification_controller import (
    FlaskInsertJustificationController,
)
from core.ports.inbound.evaluation.insert_justification_use_case import InsertJustificationCommand
 
BASE_URL = "/sessions/session-1/assets/asset-1/requirements/REQ-1/justification"
 
 
@pytest.fixture(scope="module")
def app_and_mock():
    mock_use_case = MagicMock()
    controller=FlaskInsertJustificationController(mock_use_case)
    flask_app = Flask(__name__)
    blueprint = blueprints.Blueprint("evaluation", __name__)
    controller.register_routes(blueprint)
    flask_app.register_blueprint(blueprint)
    flask_app.config["TESTING"] = True
    return flask_app, mock_use_case

@pytest.fixture()
def app(app_and_mock):
    flask_app, mock_use_case = app_and_mock
    mock_use_case.reset_mock()
    return flask_app, mock_use_case
 
 
class TestFlaskInsertJustificationController:
 
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
 