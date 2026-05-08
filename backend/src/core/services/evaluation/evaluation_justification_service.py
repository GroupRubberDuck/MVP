from core.ports.inbound.evaluation.evaluation_session.insert_justification_use_case import InsertJustificationUseCase
from core.ports.outbound.evaluation.get_session_port import GetSessionPort
from core.ports.outbound.evaluation.save_session_port import SaveSessionPort
from core.services.evaluation.insert_justification_command import InsertJustificationCommand
 
 
class EvaluationJustificationService(InsertJustificationUseCase):
 
    def __init__(
        self,
        get_session_port: GetSessionPort,
        save_session_port: SaveSessionPort,
    ) -> None:
        self._get_session = get_session_port
        self._save_session = save_session_port
 
    def insert_justification(self, command: InsertJustificationCommand) -> None:
        session = self._get_session.get_session(command.session_id)
 
        session.insert_justification(
            asset_id=command.asset_id,
            requirement_id=command.requirement_id,
            node_id=command.node_id,
            justification=command.justification,
        )
 
        self._save_session.save_session(session)
 