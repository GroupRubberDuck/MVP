from core.domain.evaluation_engine.evaluation_detail import (
    AssetEvaluationDetail,
    RequirementEvaluationDetail,
)
from core.domain.utilities.evaluation_detail_builder import EvaluationDetailBuilder
from core.domain.evaluation_engine.evaluation_engine import EvaluationEngine
from core.domain.evaluation_engine.evaluation_result import RequirementEvaluationResult
from core.domain.evaluation_object.exceptions import AssetNotFoundError
from core.domain.evaluation_standard.requirement import Requirement
from core.ports.inbound.asset.exceptions import GetAssetDetailFailure
from core.ports.inbound.asset.get_asset_evaluation_detail_use_case import GetAssetEvaluationDetailCommand, GetAssetEvaluationDetailUseCase
from core.ports.outbound.evaluation.exceptions import EvaluationSessionNotFoundError
from core.ports.outbound.evaluation.get_evaluation_session_port import GetEvaluationSessionPort


class GetAssetEvaluationDetailUseCaseService(GetAssetEvaluationDetailUseCase):
    def __init__(
        self, get_evaluation_session_port: GetEvaluationSessionPort, evaluation_engine: EvaluationEngine
    ) -> None:
        self._get_evaluation_session_port = get_evaluation_session_port
        self._evaluation_engine = evaluation_engine

    def get_asset(self, command: GetAssetEvaluationDetailCommand) -> AssetEvaluationDetail:
        try:
            session = self._get_evaluation_session_port.get_evaluation_session(command.session_id)
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
        return EvaluationDetailBuilder().build_requirement_detail(
            req=req,
            result=r
        )
