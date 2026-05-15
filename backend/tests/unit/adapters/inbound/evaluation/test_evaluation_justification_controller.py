import json
import pytest
from unittest.mock import MagicMock
from flask import Flask, blueprints
 
from adapters.inbound.evaluation.evaluation_justification_controller import (
    EvaluationJustificationController,
)
from core.ports.inbound.evaluation.insert_justification_use_case import InsertJustificationCommand
 
BASE_URL = "/sessions/session-1/assets/asset-1/requirements/REQ-1/justification"
 
 
@pytest.fixture(scope="module")
def app_and_mock():
    mock_use_case = MagicMock()
    controller=EvaluationJustificationController(mock_use_case)
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
 
 
class TestEvaluationJustificationController:
 
    def test_risponde_200_con_payload_corretto(self, app):
        """
        Dato un payload JSON valido contenente la giustificazione (Given),
        quando viene effettuata una richiesta PUT all'endpoint della giustificazione (When),
        allora il controller deve completare l'operazione e restituire uno status code 200 OK (Then).
        """
        flask_app, _ = app
        with flask_app.test_client() as client:
            response = client.put(BASE_URL, json={"justification": "testo"})
 
        assert response.status_code == 200
 
    def test_chiama_use_case_una_volta(self, app):
        """
        Dato un payload valido per l'inserimento o l'aggiornamento della giustificazione (Given),
        quando la richiesta HTTP viene processata (When),
        allora lo use case delegato all'inserimento della giustificazione deve essere invocato esattamente una volta (Then).
        """
        flask_app, mock_use_case = app
        with flask_app.test_client() as client:
            client.put(BASE_URL, json={"justification": "testo"})
 
        mock_use_case.insert_justification.assert_called_once()
 
    def test_command_ha_i_campi_corretti(self, app):
        """
        Dati gli ID estratti dai parametri dell'URL e un testo di giustificazione estratto dal body (Given),
        quando il controller costruisce il comando (When),
        allora il Command passato allo use case deve contenere l'esatta mappatura di session_id, asset_id, requirement_id e justification (Then).
        """
        flask_app, mock_use_case = app
        with flask_app.test_client() as client:
            client.put(BASE_URL, json={"justification": "testo giustificazione"})
 
        command: InsertJustificationCommand = mock_use_case.insert_justification.call_args[0][0]
        assert command.session_id == "session-1"
        assert command.asset_id == "asset-1"
        assert command.requirement_id == "REQ-1"
        assert command.justification == "testo giustificazione"
 
    def test_body_senza_justification_usa_stringa_vuota(self, app):
        """
        Dato un payload JSON che non include la chiave 'justification' (Given),
        quando viene effettuata la richiesta PUT (When),
        allora il controller deve gestire l'assenza del campo impostando una stringa vuota di default nel Command (Then).
        """
        flask_app, mock_use_case = app
        with flask_app.test_client() as client:
            client.put(BASE_URL, json={})
 
        command: InsertJustificationCommand = mock_use_case.insert_justification.call_args[0][0]
        assert command.justification == ""
 
    def test_risposta_contiene_messaggio(self, app):
        """
        Data un'operazione di salvataggio della giustificazione conclusa con successo (Given),
        quando il controller formatta la risposta (When),
        allora il body della risposta JSON deve contenere una chiave 'message' di conferma (Then).
        """
        flask_app, _ = app
        with flask_app.test_client() as client:
            response = client.put(BASE_URL, json={"justification": "testo"})
 
        body = json.loads(response.data)
        assert "message" in body
 