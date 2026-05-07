from core.domain.evaluation_engine.evaluation_detail import RequirementEvaluationDetail
from core.domain.evaluation_engine.evaluation_engine import EvaluationEngine
from core.domain.evaluation_engine.evaluation_result import RequirementEvaluationResult
from core.domain.evaluation_standard.requirement import Requirement
from core.ports.inbound.asset.exceptions import GetRequirementEvaluationDetailFailure
from core.ports.inbound.asset.get_requirement_evaluation_detail_use_case import (
    GetRequirementEvaluationDetailCommand,
    GetRequirementEvaluationDetailUseCase,
)
from core.ports.outbound.evaluation.exceptions import SessionNotFoundError
from core.ports.outbound.evaluation.get_session_port import GetSessionPort


class GetRequirementEvaluationDetailService(GetRequirementEvaluationDetailUseCase):
    def __init__(self, get_session_port: GetSessionPort, evaluation_engine: EvaluationEngine) -> None:
        self._get_session_port = get_session_port
        self._evaluation_engine = evaluation_engine

    def get_evaluation_detail(
        self, command: GetRequirementEvaluationDetailCommand
    ) -> RequirementEvaluationDetail:
        try:
            session = self._get_session_port.get_session(command.session_id)
        except SessionNotFoundError:
            raise GetRequirementEvaluationDetailFailure(
                f"Sessione '{command.session_id}' non trovata."
            )

        device_result = self._evaluation_engine.evaluate(session.device, session.standard)

        asset_result = device_result.get_asset_result(command.asset_id)
        if asset_result is None:
            raise GetRequirementEvaluationDetailFailure(
                f"Asset '{command.asset_id}' non trovato nel dispositivo."
            )

        requirement_result = asset_result.get_requirement_result(command.requirement_id)
        if requirement_result is None:
            raise GetRequirementEvaluationDetailFailure(
                f"Requisito '{command.requirement_id}' non trovato nell'asset."
            )

        req = session.standard.get_requirement(command.requirement_id)

        return self._build_detail(requirement_result, req)

    def _build_detail(
        self, r: RequirementEvaluationResult, req: Requirement
    ) -> RequirementEvaluationDetail:
        if req.decision_tree is None:
            raise GetRequirementEvaluationDetailFailure(
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