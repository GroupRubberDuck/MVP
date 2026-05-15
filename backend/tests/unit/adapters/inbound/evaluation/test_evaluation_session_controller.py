import pytest
from unittest.mock import MagicMock
from flask import Flask, Blueprint
from adapters.inbound.evaluation.evaluation_session_controller import (
    EvaluationSessionController
    ) 



@pytest.fixture
def app():
    mock_open = MagicMock()
    mock_close = MagicMock()
    mock_save = MagicMock()
    mock_commit = MagicMock()
    mock_get_active = MagicMock()
    mock_controller=EvaluationSessionController(mock_open, mock_close, mock_commit, mock_get_active)
    flask_app = Flask(__name__)
    bp=Blueprint("evaluation_session",__name__)
    mock_controller.register_routes(bp)
    flask_app.register_blueprint(bp)
    flask_app.config["TESTING"] = True
    return flask_app, mock_open, mock_close, mock_save, mock_commit, mock_get_active


class TestCloseSession:

    def test_risponde_200(self, app):
        """
        Dato un ID di sessione valido (Given),
        quando viene inviata una richiesta DELETE per chiudere la sessione di valutazione (When),
        allora il controller deve completare l'operazione con successo e restituire uno status code 200 OK (Then).
        """
        flask_app, _, mock_close, _, _, _ = app
        with flask_app.test_client() as client:
            response = client.delete("/sessions/session-1")

        assert response.status_code == 200

    def test_chiama_use_case_con_session_id_corretto(self, app):
        """
        Dato un parametro session_id presente nell'URL (Given),
        quando il controller elabora la richiesta di chiusura (When),
        allora deve estrarre correttamente l'ID, mapparlo nel relativo Command e passarlo allo use case responsabile (Then).
        """
        flask_app, _, mock_close, _, _, _ = app
        with flask_app.test_client() as client:
            client.delete("/sessions/session-1")

        command = mock_close.close_evaluation_session.call_args[0][0]
        assert command.session_id == "session-1"


class TestCommitAndClose:

    def test_risponde_200(self, app):
        """
        Dato un ID di sessione associato a un'operazione di salvataggio e chiusura definitiva (Given),
        quando viene effettuata una richiesta POST all'endpoint di commit-and-close (When),
        allora il controller deve confermare il termine dell'operazione restituendo uno status code 200 OK (Then).
        """
        flask_app, _, _, _, mock_commit, _ = app
        with flask_app.test_client() as client:
            response = client.post("/sessions/session-1/commit-and-close")

        assert response.status_code == 200

    def test_chiama_commit_poi_close(self, app):
        """
        Dato un ID di sessione valido (Given),
        quando l'utente invoca la rotta aggregata per eseguire il commit e la chiusura simultaneamente (When),
        allora il controller deve garantire l'ordine sequenziale delle operazioni: prima chiamare lo use case di commit per salvare i dati, e solo dopo invocare lo use case di chiusura (Then).
        """
        flask_app, _, mock_close, _, mock_commit, _ = app
        call_order = []
        mock_commit.commit.side_effect = lambda _: call_order.append("commit")
        mock_close.close_evaluation_session.side_effect = lambda _: call_order.append("close")

        with flask_app.test_client() as client:
            client.post("/sessions/session-1/commit-and-close")

        assert call_order == ["commit", "close"]