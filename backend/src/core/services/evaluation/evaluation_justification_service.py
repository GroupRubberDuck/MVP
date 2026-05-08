from core.ports.inbound.evaluation.evaluation_session.insert_justification_use_case import InsertJustificationUseCase, InsertJustificationCommand
from core.ports.outbound.evaluation.get_evaluation_session_port import GetEvaluationSessionPort
from core.ports.outbound.evaluation.save_evaluation_session_port import SaveEvaluationSessionPort
from core.ports.outbound.evaluation.exceptions import (EvaluationSessionNotFoundError,
                                                        EvaluationSessionSaveError)
from core.ports.inbound.evaluation.exceptions import InsertJustificationFailure
from core.domain.evaluation_object.exceptions import AssetNotFoundError
 
class EvaluationJustificationService(InsertJustificationUseCase):
    def __init__(self, 
                 get_evaluation_session_port: GetEvaluationSessionPort, 
                 save_evaluation_session_port: SaveEvaluationSessionPort
                 ):
        self.get_evaluation_session_port = get_evaluation_session_port
        self.save_evaluation_session_port = save_evaluation_session_port
 
    def insert_justification(self, command: InsertJustificationCommand) -> None:
        
        try:
            session = self.get_evaluation_session_port.get_evaluation_session(command.session_id)
        except EvaluationSessionNotFoundError as e:
            raise InsertJustificationFailure(f"Errore durante il recupero della sessione: {str(e)}")
        
        
        try:
            session.device.get_asset(command.asset_id).set_justification(
                command.requirement_id, command.justification
            )
        except AssetNotFoundError as e:
            raise InsertJustificationFailure(f"Errore durante il recupero dell'asset: {str(e)}")
        
        try:
            self.save_evaluation_session_port.save_evaluation_session(session)
        except EvaluationSessionSaveError as e:
            raise InsertJustificationFailure(f"Errore durante il salvataggio della sessione: {str(e)}")
 