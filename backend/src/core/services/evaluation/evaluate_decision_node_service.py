from core.ports.inbound.evaluation.evaluate_decision_node_use_case import (
    EvaluateDecisionNodeUseCase,
    EvaluateDecisionNodeCommand,
)
from core.ports.inbound.evaluation.exceptions import EvaluateNodeFailure
from core.ports.outbound.evaluation.get_evaluation_session_port import GetEvaluationSessionPort
from core.ports.outbound.evaluation.evaluation_session.save_evaluation_session_port import SaveEvaluationSessionPort
from core.ports.outbound.evaluation.exceptions import EvaluationSessionNotFoundError
from core.domain.evaluation_object.exceptions import AssetNotFoundError
from core.ports.outbound.evaluation.exceptions import EvaluationSessionSaveError

class EvaluateDecisionNodeService(EvaluateDecisionNodeUseCase):
    def __init__(
        self,
        get_evaluation_session_port: GetEvaluationSessionPort,
        save_evaluation_session_port: SaveEvaluationSessionPort,
    ) -> None:
        self._get_session = get_evaluation_session_port
        self._save_session = save_evaluation_session_port

    def evaluate_node(self, command: EvaluateDecisionNodeCommand) -> None:
        try:
            session = self._get_session.get_evaluation_session(command.session_id)
        except EvaluationSessionNotFoundError as e:
            raise EvaluateNodeFailure(
                f"Impossibile valutare il nodo: Sessione '{command.session_id}' non trovata."
            ) from e
        
        try:
            asset = session.device.get_asset(command.asset_id)
        except AssetNotFoundError as e:
            raise EvaluateNodeFailure(
                f"Impossibile valutare il nodo: Asset '{command.asset_id}' non trovato nella sessione."
            ) from e
        
        try:
            asset.set_node_choice(
                requirement_id=command.requirement_id, 
                node_id=command.node_id, 
                value=command.answer
            )
        except ValueError as e:
            raise EvaluateNodeFailure(f"Risposta non valida per il nodo: {str(e)}") from e

        try:
            self._save_session.save_evaluation_session(session)
        except EvaluationSessionSaveError as e:
            raise EvaluateNodeFailure(
                f"Errore durante il salvataggio della valutazione: {str(e)}"
            ) from e