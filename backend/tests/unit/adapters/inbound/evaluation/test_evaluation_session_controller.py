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
    mock_controller=EvaluationSessionController(mock_open, mock_close, mock_commit)
    flask_app = Flask(__name__)
    bp=Blueprint("evaluation_session",__name__)
    mock_controller.register_routes(bp)
    flask_app.register_blueprint(bp)
    flask_app.config["TESTING"] = True
    return flask_app, mock_open, mock_close, mock_save, mock_commit


class TestCloseSession:

    def test_risponde_200(self, app):
        flask_app, _, mock_close, _, _ = app
        with flask_app.test_client() as client:
            response = client.delete("/sessions/session-1")

        assert response.status_code == 200

    def test_chiama_use_case_con_session_id_corretto(self, app):
        flask_app, _, mock_close, _, _ = app
        with flask_app.test_client() as client:
            client.delete("/sessions/session-1")

        command = mock_close.close_evaluation_session.call_args[0][0]
        assert command.session_id == "session-1"


class TestCommitAndClose:

    def test_risponde_200(self, app):
        flask_app, _, _, _, mock_commit = app
        with flask_app.test_client() as client:
            response = client.post("/sessions/session-1/commit-and-close")

        assert response.status_code == 200

    def test_chiama_commit_poi_close(self, app):
        flask_app, _, mock_close, _, mock_commit = app
        call_order = []
        mock_commit.commit.side_effect = lambda _: call_order.append("commit")
        mock_close.close_evaluation_session.side_effect = lambda _: call_order.append("close")

        with flask_app.test_client() as client:
            client.post("/sessions/session-1/commit-and-close")

        assert call_order == ["commit", "close"]