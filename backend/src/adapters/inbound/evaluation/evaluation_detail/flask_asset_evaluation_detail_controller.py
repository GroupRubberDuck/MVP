from adapters.inbound.flask_controller_interface import FlaskController


from core.ports.inbound.asset.get_asset_detail_use_case import (
    GetAssetDetailCommand,
    GetAssetDetailUseCase,
)

from core.domain.evaluation_engine.evaluation_detail import (
    AssetEvaluationDetail,
)
from flask import Blueprint, render_template
from flask.typing import ResponseReturnValue

from core.domain.evaluation_object.asset import AssetType
from core.domain.evaluation_engine.evaluation_result import EvaluationState

from core.ports.inbound.asset.exceptions import GetAssetDetailFailure
from pydantic import BaseModel, ValidationError

# DTOs


class RequirementEvaluationSummaryDTO(BaseModel):
    id: str
    evaluation: EvaluationState


class AssetEvaluationDTO(BaseModel):
    name: str
    type: AssetType
    evaluation: EvaluationState
    description: str
    requirements: tuple[RequirementEvaluationSummaryDTO, ...]


# controller


class FlaskAssetEvaluationDetailController(FlaskController):
    def __init__(self, get_asset_ev_detail_use_case: GetAssetDetailUseCase) -> None:
        self._get_asset_ev_detail_use_case = get_asset_ev_detail_use_case

    def _make_dto(self, detail: AssetEvaluationDetail) -> AssetEvaluationDTO:
        return AssetEvaluationDTO(
            name=detail.name,
            type=detail.asset_type,
            evaluation=detail.verdict,
            description=detail.description,
            requirements=tuple(
                RequirementEvaluationSummaryDTO(
                    id=req.requirement_id,
                    evaluation=req.state,
                )
                for req in detail.requirement_details
            ),
        )

    def register_routes(self, blueprint: Blueprint) -> None:
        @blueprint.route(
            "/sessions/<session_id>/devices/<device_id>/assets/<asset_id>",
            methods=["GET"],
        )
        def get_asset_evaluation_detail(
            session_id: str, device_id: str, asset_id: str
        ) -> ResponseReturnValue:
            try:
                command = GetAssetDetailCommand(
                    asset_id=asset_id, device_id=device_id, session_id=session_id
                )
            except ValidationError as e:
                return render_template(
                    "errors/400.html",
                    message=f"I parametri forniti non sono validi: {e}",
                ), 400

            try:
                asset = self._get_asset_ev_detail_use_case.get_asset(command)
            except GetAssetDetailFailure as e:
                return render_template(
                    "errors/404.html",
                    message=f"Risorsa non trovata: {e}",
                ), 404

            asset_dto = self._make_dto(asset)

            return render_template("layouts/asset_detail.html", asset=asset_dto.model_dump()), 200
