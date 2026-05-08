from core.ports.inbound.evaluation.set_justification_use_case import SetJustificationCommand, SetJustificationUseCase

from core.ports.outbound.evaluation.get_evaluation_session_port import GetEvaluationSessionPort
from core.ports.outbound.evaluation.save_evaluation_session_port import SaveEvaluationSessionPort
from core.ports.outbound.evaluation.exceptions import EvaluationSessionNotFoundError, EvaluationSessionSaveError
from core.ports.inbound.evaluation.exceptions import SetJustificationFailure
from core.domain.evaluation_object.exceptions import AssetNotFoundError

class SetJustificationService(SetJustificationUseCase):
    def __init__(self, 
                 get_evaluation_session_port: GetEvaluationSessionPort, 
                 save_evaluation_session_port: SaveEvaluationSessionPort
                 ):
        self.get_evaluation_session_port = get_evaluation_session_port
        self.save_evaluation_session_port = save_evaluation_session_port

    def set_justification(self, command: SetJustificationCommand) -> None:
        # Recupera la sessione di valutazione
        try:
            session = self.get_evaluation_session_port.get_evaluation_session(command.session_id)
        except EvaluationSessionNotFoundError as e:
            raise SetJustificationFailure(f"Errore durante il recupero della sessione: {str(e)}")
        

        # Verifica che l'asset sia presente nella sessione
        try:
            asset = session.device.get_asset(command.asset_id)
        except AssetNotFoundError as e:
            raise SetJustificationFailure(f"Errore durante il recupero dell'asset: {str(e)}")
        
        # Imposta la giustificazione per il requisito specificato
        try:
            asset.set_justification(command.requirement_id, command.justification)
        except Exception as e:
            raise SetJustificationFailure(f"Errore durante l'impostazione della giustificazione: {str(e)}")
        
        # Salva la sessione aggiornata
        try:
            self.save_evaluation_session_port.save_evaluation_session(session)
        except EvaluationSessionSaveError as e:
            raise SetJustificationFailure(f"Errore durante il salvataggio della sessione: {str(e)}")