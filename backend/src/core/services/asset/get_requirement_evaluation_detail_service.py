from core.domain.evaluation_engine.evaluation_detail import RequirementEvaluationDetail
from core.domain.evaluation_engine.evaluation_engine import EvaluationEngine
from core.domain.evaluation_engine.evaluation_result import RequirementEvaluationResult
from core.domain.evaluation_standard.requirement import Requirement
from core.ports.inbound.asset.exceptions import GetRequirementEvaluationDetailFailure
from core.ports.inbound.asset.get_requirement_evaluation_detail_use_case import (
    GetRequirementEvaluationDetailCommand,
    GetRequirementEvaluationDetailUseCase,
)
from core.ports.outbound.evaluation.exceptions import EvaluationSessionNotFoundError
from core.ports.outbound.evaluation.get_evaluation_session_port import GetEvaluationSessionPort


from core.domain.utilities.evaluation_detail_builder import EvaluationDetailBuilder

class GetRequirementEvaluationDetailService(GetRequirementEvaluationDetailUseCase):
 
    def __init__(
        self,
        get_evaluation_session_port: GetEvaluationSessionPort,
        evaluation_engine: EvaluationEngine,
    ) -> None:
        self._get_evaluation_session_port = get_evaluation_session_port
        self._evaluation_engine = evaluation_engine
 
    def get_evaluation_detail(
        self, command: GetRequirementEvaluationDetailCommand
    ) -> RequirementEvaluationDetail:
        try:
            session = self._get_evaluation_session_port.get_evaluation_session(
                command.session_id
            )
        except EvaluationSessionNotFoundError:
            raise GetRequirementEvaluationDetailFailure(
                f"Sessione '{command.session_id}' non trovata."
            )
 
        if session.device.id != command.device_id:
            raise GetRequirementEvaluationDetailFailure(
                f"Il dispositivo '{command.device_id}' non è associato alla sessione."
            )
 
        device_result = self._evaluation_engine.evaluate(
            session.device, session.standard
        )
 
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
        return EvaluationDetailBuilder().build_requirement_detail(
            result=r,
            req=req
        )