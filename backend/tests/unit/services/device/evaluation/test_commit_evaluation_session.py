import pytest
from unittest.mock import MagicMock

from core.services.evaluation.evaluation_session.commit_evaluation_session_service import CommitEvaluationSessionService
from core.ports.inbound.evaluation.evaluation_session.commit_evaluation_session_use_case import CommitEvaluationSessionCommand
from core.ports.inbound.evaluation.exceptions import CommitSessionFailure
from core.ports.outbound.evaluation.exceptions import EvaluationSessionNotFoundError
from core.ports.outbound.device.exceptions import DeviceSaveError


def make_command(session_id="session-123") -> CommitEvaluationSessionCommand:
    return CommitEvaluationSessionCommand(session_id=session_id)

def make_service():
    mock_get_session_port = MagicMock()
    mock_save_device_port = MagicMock()
    mock_session = MagicMock()

    mock_get_session_port.get_evaluation_session.return_value = mock_session

    service = CommitEvaluationSessionService(
        get_evaluation_session_port=mock_get_session_port,
        save_device_port=mock_save_device_port
    )

    return service, mock_get_session_port, mock_save_device_port, mock_session


class TestCommitEvaluationSessionService:

    def test_commit_effettuato_con_successo(self):
        
        service, mock_get_session, mock_save_device, mock_session = make_service()
        command = make_command(session_id="session-1")
        
        service.commit(command)
        
        # Verifichiamo che la sessione sia stata richiesta con l'ID corretto
        mock_get_session.get_evaluation_session.assert_called_once_with("session-1")
        
        # Verifichiamo che il salvataggio sia avvenuto passando ESATTAMENTE il device della sessione
        mock_save_device.save_device.assert_called_once_with(mock_session.device)

    def test_solleva_failure_se_sessione_non_trovata(self):
        
        service, mock_get_session, _, _ = make_service()
        
        mock_get_session.get_evaluation_session.side_effect = EvaluationSessionNotFoundError("Cache vuota")

        with pytest.raises(CommitSessionFailure) as exc_info:
            service.commit(make_command(session_id="session-fake"))

        # Verifichiamo che l'errore sia stato tradotto correttamente
        assert "Sessione 'session-fake' non trovata" in str(exc_info.value)

    def test_solleva_failure_se_salvataggio_device_fallisce(self):
        
        service, _, mock_save_device, _ = make_service()
        
        mock_save_device.save_device.side_effect = DeviceSaveError("Database offline")
         
        with pytest.raises(CommitSessionFailure) as exc_info:
            service.commit(make_command())

        # Verifichiamo che l'errore contenga il nostro messaggio di dominio
        assert "Errore critico durante il salvataggio del device" in str(exc_info.value)
        assert "Database offline" in str(exc_info.value)