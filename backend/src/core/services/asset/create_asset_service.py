import uuid
from core.domain.evaluation_object.asset.asset import Asset
from core.domain.evaluation_object.asset.asset_anagraphic import AssetAnagraphic
from core.domain.evaluation_object.asset.asset_proprieties import AssetProprieties
from core.domain.session.evaluation_session import EvaluationSession
from core.ports.inbound.asset.create_asset_use_case import CreateAssetUseCase, CreateAssetCommand
from core.ports.outbound.evaluation.get_evaluation_session_port import GetEvaluationSessionPort
from core.ports.outbound.evaluation.save_evaluation_session_port import SaveEvaluationSessionPort
from core.ports.outbound.evaluation.exceptions import EvaluationSessionNotFoundError, EvaluationSessionSaveError
from core.services.asset.exceptions import AssetCreationFailure

class CreateAssetService(CreateAssetUseCase):

    def __init__(
        self,
        get_session: GetEvaluationSessionPort,
        save_session: SaveEvaluationSessionPort,
    ):
        self._get_session = get_session
        self._save_session = save_session

    def create_asset(self, command: CreateAssetCommand) -> str:
        try:
            session: EvaluationSession = self._get_session.get_evaluation_session(
                command.session_id
            )
        except EvaluationSessionNotFoundError:
            raise AssetCreationFailure("Session not found") from None

        try:
            anagraphic = AssetAnagraphic(
                name=command.name,
                asset_type=command.asset_type,
                description=command.description,
            )
    
            asset = Asset(
                id=str(uuid.uuid4()),
                anagraphic=anagraphic,
                proprieties=AssetProprieties(),
            )
    
            session.device.add_asset(asset)
        except Exception as e:
            raise AssetCreationFailure("Failed to create asset") from e
        try:
            self._save_session.save_evaluation_session(session)
        except EvaluationSessionSaveError as e:
            raise AssetCreationFailure("Failed to save evaluation session") from e

        return asset.id