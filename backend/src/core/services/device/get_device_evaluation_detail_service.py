from core.domain.evaluation_engine.evaluation_detail import (
    DeviceEvaluationDetail,
    AssetEvaluationDetail,
    RequirementEvaluationDetail,
)
from core.domain.utilities.evaluation_detail_builder import EvaluationDetailBuilder
from core.domain.evaluation_engine.evaluation_engine import EvaluationEngine
from core.domain.evaluation_engine.evaluation_result import (
    AssetEvaluationResult,
    RequirementEvaluationResult,
)
from core.domain.session.evaluation_session import EvaluationSession
from core.domain.evaluation_standard.requirement import Requirement
from core.ports.inbound.device.get_device_evaluation_detail_use_case import (
    GetDeviceEvaluationDetailCommand,
    GetDeviceEvaluationDetailUseCase,
)

from core.ports.inbound.evaluation.exceptions import GetEvaluationDetailFailure
from core.ports.outbound.evaluation.exceptions import EvaluationSessionNotFoundError
from core.ports.outbound.evaluation.get_evaluation_session_port import GetEvaluationSessionPort


class GetDeviceEvaluationDetailService(GetDeviceEvaluationDetailUseCase):
    def __init__(
        self, 
        get_evaluation_session_port: GetEvaluationSessionPort, 
        evaluation_engine: EvaluationEngine
    ) -> None:
        self._get_evaluation_session_port = get_evaluation_session_port
        self._evaluation_engine = evaluation_engine

    def get_device_evaluation_detail(
        self, command: GetDeviceEvaluationDetailCommand
    ) -> DeviceEvaluationDetail:
        try:
            session = self._get_evaluation_session_port.get_evaluation_session(command.session_id)
        except EvaluationSessionNotFoundError:
            raise GetEvaluationDetailFailure(
                f"Sessione '{command.session_id}' non trovata."
            )
        
        device_result = self._evaluation_engine.evaluate(
            session.device, session.standard
        )

        asset_details = tuple(
            self._make_asset_detail(asset_result, session)
            for asset_result in device_result.asset_results
        )

        return DeviceEvaluationDetail(
            device_id=session.device.id,
            name=session.device.name,
            operating_system=session.device.os,
            description=session.device.description,
            standard_id=session.device.standard_id,
            asset_details=asset_details,
            verdict=device_result.verdict,
        )

    def _make_asset_detail(
        self, asset_result: AssetEvaluationResult, session: EvaluationSession
    ) -> AssetEvaluationDetail:
        asset = session.device.get_asset(asset_result.asset_id)
        
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
        return EvaluationDetailBuilder().build_requirement_detail(
            req=req,
            result=r
        )