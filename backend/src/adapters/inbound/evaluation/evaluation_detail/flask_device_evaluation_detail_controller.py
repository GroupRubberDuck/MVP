from flask import Blueprint, render_template
from flask.typing import ResponseReturnValue
from pydantic import BaseModel, ValidationError

from adapters.inbound.flask_controller_interface import FlaskController
from core.ports.inbound.device.get_device_evaluation_detail_use_case import (
    GetDeviceEvaluationDetailUseCase,
    GetDeviceEvaluationDetailCommand
)
from core.domain.evaluation_engine.evaluation_detail import DeviceEvaluationDetail
from core.domain.evaluation_object.asset import AssetType
from core.domain.evaluation_engine.evaluation_result import EvaluationState
from core.ports.inbound.evaluation.exceptions import GetEvaluationDetailFailure

# --- DTOs ---
class AssetEvaluationSummaryDTO(BaseModel):
    asset_id: str
    asset_name: str
    asset_type: AssetType
    asset_evaluation: EvaluationState

class DeviceEvaluationDTO(BaseModel):
    device_name: str
    device_os: str
    device_description: str
    device_evaluation_result: EvaluationState
    asset_list: tuple[AssetEvaluationSummaryDTO, ...]

# --- Controller ---
class FlaskDeviceEvaluationDetailController(FlaskController):
    def __init__(self, get_device_ev_detail_use_case: GetDeviceEvaluationDetailUseCase):
        self._get_device_ev_detail_use_case = get_device_ev_detail_use_case

    def _make_dto(self, detail: DeviceEvaluationDetail) -> DeviceEvaluationDTO:
        return DeviceEvaluationDTO(
            device_name=detail.name,
            device_os=detail.operating_system,
            device_description=detail.description,
            device_evaluation_result=detail.verdict,
            asset_list=tuple(
                AssetEvaluationSummaryDTO(
                    asset_id=asset.asset_id,
                    asset_name=asset.name,
                    asset_type=asset.asset_type,
                    asset_evaluation=asset.verdict
                ) for asset in detail.asset_details
            )
        )

    def register_routes(self, blueprint: Blueprint) -> None:
        @blueprint.route("/sessions/<session_id>/devices/<device_id>", methods=["GET"])
        def get_device_evaluation_detail(session_id: str, device_id: str) -> ResponseReturnValue:
            try:
                command = GetDeviceEvaluationDetailCommand(
                    session_id=session_id, 
                    device_id=device_id
                )
            except ValidationError as e:
                return render_template(
                    "errors/400.html", 
                    message=f"I parametri forniti non sono validi: {e}"
                ), 400
            

            try:
                device_eval_detail = self._get_device_ev_detail_use_case.get_device_evaluation_detail(command)
            except GetEvaluationDetailFailure as e:
                return render_template("errors/404.html", message=f"Risorsa non trovata: {e}"), 404
            
            dto = self._make_dto(device_eval_detail)
            return render_template("layouts/device_eval_detail.html", device_detail=dto.model_dump()), 200