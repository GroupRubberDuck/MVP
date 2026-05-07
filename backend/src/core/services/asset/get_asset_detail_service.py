from core.domain.evaluation_engine.evaluation_detail import AssetEvaluationDetail, RequirementEvaluationDetail
from core.domain.evaluation_engine.evaluation_engine import EvaluationEngine
from core.domain.evaluation_object.exceptions import AssetNotFoundError
from core.ports.inbound.asset.exceptions import GetAssetDetailFailure
from core.ports.inbound.asset.get_asset_detail_use_case import GetAssetDetailCommand, GetAssetDetailUseCase
from core.ports.outbound.evaluation.exceptions import SessionNotFoundError
from core.ports.outbound.evaluation.get_session_port import GetSessionPort


class GetAssetDetailService(GetAssetDetailUseCase):
    def __init__(self, get_session_port: GetSessionPort, evaluation_engine: EvaluationEngine) -> None:
        self._get_session_port = get_session_port
        self._evaluation_engine = evaluation_engine

    def get_asset(self, command: GetAssetDetailCommand) -> AssetEvaluationDetail:
        try:
            session = self._get_session_port.get_session(command.session_id)
        except SessionNotFoundError:
            raise GetAssetDetailFailure(
                f"Sessione '{command.session_id}' non trovata."
            )

        device_result = self._evaluation_engine.evaluate(session.device, session.standard)

        asset_result = device_result.get_asset_result(command.asset_id)
        if asset_result is None:
            raise GetAssetDetailFailure(
                f"Asset '{command.asset_id}' non trovato nel dispositivo."
            )

        try:
            asset = session.device.get_asset(command.asset_id)
        except AssetNotFoundError:
            raise GetAssetDetailFailure(
                f"Asset '{command.asset_id}' non trovato nel dispositivo."
            )

        requirement_details = tuple(
            RequirementEvaluationDetail(
                requirement_id=r.requirement_id,
                name=session.standard.get_requirement(r.requirement_id).name,
                description=session.standard.get_requirement(r.requirement_id).description,
                target=session.standard.get_requirement(r.requirement_id).target_description,
                justification=r.justification,
                node_choices=r.node_choices,
                state=r.state,
                dependencies=r.dependencies,
            )
            for r in asset_result.requirement_results
        )

        return AssetEvaluationDetail(
            asset_id=asset.id,
            name=asset.anagraphic.name,
            asset_type=asset.anagraphic.asset_type,
            description=asset.anagraphic.description,
            requirement_details=requirement_details,
            verdict=asset_result.verdict,
        )