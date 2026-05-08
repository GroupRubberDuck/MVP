from core.domain.evaluation_engine.evaluation_detail import (
    AssetEvaluationDetail,
    RequirementEvaluationDetail,
)
from core.domain.evaluation_engine.evaluation_engine import EvaluationEngine
from core.domain.evaluation_engine.evaluation_result import RequirementEvaluationResult
from core.domain.evaluation_object.exceptions import AssetNotFoundError
from core.domain.evaluation_standard.requirement import Requirement
from core.ports.inbound.asset.exceptions import GetAssetDetailFailure
from core.ports.inbound.asset.get_asset_detail_use_case import GetAssetDetailCommand, GetAssetDetailUseCase
from core.ports.outbound.evaluation.exceptions import EvaluationSessionNotFoundError
from core.ports.outbound.evaluation.get_evaluation_session_port import GetEvaluationSessionPort


class GetAssetDetailService(GetAssetDetailUseCase):
    def __init__(
        self, get_session_port: GetEvaluationSessionPort, evaluation_engine: EvaluationEngine
    ) -> None:
        self._get_session_port = get_session_port
        self._evaluation_engine = evaluation_engine

    def get_asset(self, command: GetAssetDetailCommand) -> AssetEvaluationDetail:
        try:
            session = self._get_session_port.get_evaluation_session(command.session_id)
        except EvaluationSessionNotFoundError:
            raise GetAssetDetailFailure(
                f"Sessione '{command.session_id}' non trovata."
            )

        device_result = self._evaluation_engine.evaluate(
            session.device, session.standard
        )

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
            self._make_requirement_detail(
                r, session.standard.get_requirement(r.requirement_id)
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

    def _make_requirement_detail(
        self, r: RequirementEvaluationResult, req: Requirement
    ) -> RequirementEvaluationDetail:
        if req.decision_tree is None:
            raise GetAssetDetailFailure(
                f"Il requisito '{req.requirement_id}' non ha un albero decisionale."
            )
        return RequirementEvaluationDetail(
            requirement_id=r.requirement_id,
            name=req.name,
            description=req.description,
            target=req.target_description,
            justification=r.justification,
            node_choices=r.node_choices,
            nodes=req.decision_tree.nodes,
            state=r.state,
            dependencies=r.dependencies,
        )
