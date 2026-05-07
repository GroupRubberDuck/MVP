import uuid
from ...domain.evaluation_object.asset.asset import Asset
from ...domain.evaluation_object.asset.asset_anagraphic import AssetAnagraphic
from ...domain.evaluation_object.asset.asset_proprieties import AssetProprieties
from ...domain.session.evaluation_session import EvaluationSession
from ...ports.inbound.asset.create_asset_use_case import CreateAssetUseCase
from ...ports.outbound.evaluation.get_evaluation_session_port import GetEvaluationSessionPort
from ...ports.outbound.evaluation.save_evaluation_session_port import SaveEvaluationSessionPort
from .create_asset_command import CreateAssetCommand


class CreateAssetService(CreateAssetUseCase):

    def __init__(
        self,
        get_session: GetEvaluationSessionPort,
        save_session: SaveEvaluationSessionPort,
    ):
        self._get_session = get_session
        self._save_session = save_session

    def create_asset(self, command: CreateAssetCommand) -> bool:

        session: EvaluationSession = self._get_session.get_evaluation_session(
            command.session_id
        )

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

        self._save_session.save_evaluation_session(session)

        return True