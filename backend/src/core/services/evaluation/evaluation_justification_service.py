from core.ports.inbound.evaluation.evaluation_session.insert_justification_use_case import InsertJustificationUseCase
from core.ports.outbound.evaluation.get_session_port import GetSessionPort
from core.ports.outbound.evaluation.save_session_port import SaveSessionPort
from core.services.evaluation.insert_justification_command import InsertJustificationCommand
from core.domain.evaluation_object.exceptions import AssetNotFoundError
 
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
        try:
            session.device.get_asset(command.asset_id).set_justification(
                command.requirement_id, command.justification
            )
        except AssetNotFoundError as e:
            raise SetJustificationFailure(f"Errore durante il recupero dell'asset: {str(e)}")
        self._save_session.save_session(session)
 