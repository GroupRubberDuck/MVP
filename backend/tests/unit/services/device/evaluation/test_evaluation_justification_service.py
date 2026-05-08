from unittest.mock import MagicMock
 
from core.services.evaluation.set_justification_service import SetJustificationService
from core.services.evaluation.insert_justification_command import InsertJustificationCommand
from core.ports.inbound.evaluation.evaluation_session.insert_justification_use_case import SetJustificationService
 
 
def make_command(**kwargs) -> InsertJustificationCommand:
    defaults = dict(
        session_id="session-1",
        asset_id="asset-1",
        requirement_id="REQ-1",
        node_id="NODE-1",
        justification="testo giustificazione",
    )
    return InsertJustificationCommand(**{**defaults, **kwargs})
 
 
def make_service():
    mock_get = MagicMock()   # simula GetSessionPort
    mock_save = MagicMock()  # simula SaveSessionPort
    mock_session = MagicMock()
    mock_get.get_session.return_value = mock_session
    service = SetJustificationService(mock_get, mock_save)
    return service, mock_get, mock_save, mock_session
 
 
class TestEvaluationJustificationService:
 
    def test_recupera_la_sessione_corretta(self):
        service, mock_get, _, _ = make_service()
 
        service.insert_justification(make_command(session_id="session-1"))
 
        mock_get.get_session.assert_called_once_with("session-1")
 
    def test_chiama_insert_justification_sulla_sessione(self):
        service, _, _, mock_session = make_service()
 
        service.insert_justification(make_command())
 
        mock_session.insert_justification.assert_called_once_with(
            asset_id="asset-1",
            requirement_id="REQ-1",
            node_id="NODE-1",
            justification="testo giustificazione",
        )
 
    def test_salva_la_sessione_dopo_la_modifica(self):
        service, _, mock_save, mock_session = make_service()
 
        service.insert_justification(make_command())
 
        mock_save.save_session.assert_called_once_with(mock_session)
 
    def test_salvataggio_avviene_dopo_insert(self):
        call_order = []
        service, _, mock_save, mock_session = make_service()
        mock_session.insert_justification.side_effect = lambda **_: call_order.append("insert")
        mock_save.save_session.side_effect = lambda _: call_order.append("save")
 
        service.insert_justification(make_command())
 
        assert call_order == ["insert", "save"]