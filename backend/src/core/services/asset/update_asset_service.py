from core.ports.inbound.asset.update_asset_use_case import (
    UpdateAssetCommand,
    UpdateAssetUseCase,
)
from core.ports.outbound.evaluation.get_evaluation_session_port import GetEvaluationSessionPort
from core.ports.outbound.evaluation.save_evaluation_session_port import SaveEvaluationSessionPort
from core.ports.inbound.asset.exceptions import UpdateAssetFailure
from core.ports.outbound.evaluation.exceptions import EvaluationSessionSaveError, EvaluationSessionNotFoundError
from core.domain.evaluation_object.exceptions import AssetNotFoundError


class UpdateAssetService(UpdateAssetUseCase):
    def __init__(
        self,
        get_evaluation_session_port: GetEvaluationSessionPort,
        save_evaluation_session_port: SaveEvaluationSessionPort,
    ) -> None:
        self._get_evaluation_session_port = get_evaluation_session_port
        self._save_evaluation_session_port = save_evaluation_session_port

    def update_asset(self, update_command: UpdateAssetCommand) -> None:
        # 1. Recupero la sessione
        try:
            session = self._get_evaluation_session_port.get_evaluation_session(update_command.session_id)
        except EvaluationSessionNotFoundError as e:
            raise UpdateAssetFailure(
                f"Impossibile aggiornare l'asset: Sessione '{update_command.session_id}' non trovata."
            ) from e
        
        try: 
            session.device.get_asset(update_command.asset_id).update_anagraphic(
                name=update_command.name,
                asset_type=update_command.asset_type,
                description=update_command.description,
            )
        except AssetNotFoundError as e:
            raise UpdateAssetFailure(
                f"Impossibile aggiornare: Asset '{update_command.asset_id}' non trovato."
            ) from e
        except ValueError as e:
            raise UpdateAssetFailure(f"Dati non validi per l'asset: {str(e)}") from e
        
        try:
            self._save_evaluation_session_port.save_evaluation_session(session)
        except EvaluationSessionSaveError as e:
            raise UpdateAssetFailure(
                f"Errore durante il salvataggio della sessione dopo l'aggiornamento dell'asset: {str(e)}"
            ) from e
