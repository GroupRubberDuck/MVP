from unittest.mock import MagicMock
from core.services.evaluation.evaluation_session.close_evaluation_session_service import CloseEvaluationSessionService
from core.ports.inbound.evaluation.evaluation_session.close_evaluation_session_use_case import CloseEvaluationSessionCommand


def make_service():
    mock_delete = MagicMock()
    service = CloseEvaluationSessionService(mock_delete)
    return service, mock_delete


class TestCloseEvaluationSessionService:

    def test_chiama_delete_con_session_id_corretto(self):
        service, mock_delete = make_service()
        command = CloseEvaluationSessionCommand(session_id="session-1")

        service.close_evaluation_session(command)

        mock_delete.close_evaluation_session.assert_called_once_with("session-1")