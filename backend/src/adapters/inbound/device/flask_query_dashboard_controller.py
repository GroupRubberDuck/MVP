from core.ports.inbound.device.get_device_evaluation_detail_use_case import (
    GetDeviceEvaluationDetailUseCase,
    GetDeviceEvaluationDetailCommand,
)
from core.ports.inbound.evaluation.exceptions import GetEvaluationDetailFailure
from adapters.inbound.flask_controller_interface import FlaskController
from flask import Blueprint, render_template
from flask.typing import ResponseReturnValue
from core.domain.evaluation_standard.evaluation_state import EvaluationState
from core.domain.evaluation_object.asset.asset_type import AssetType
from pydantic import BaseModel, ValidationError


class AssetSummaryDTO(BaseModel):
    asset_id: str
    name: str
    type: AssetType
    aggregate_status: EvaluationState


class DeviceDashboardDTO(BaseModel):
    device_id: str
    device_name: str
    operating_system: str
    description: str
    aggregate_status: EvaluationState
    asset_list: list[AssetSummaryDTO]


class FlaskQueryDashboardController(FlaskController):
    def __init__(
        self,
        get_device_evaluation_detail_use_case: GetDeviceEvaluationDetailUseCase,
    ) -> None:
        self._get_device_evaluation_detail_use_case = (
            get_device_evaluation_detail_use_case
        )

    def register_routes(self, blueprint: Blueprint) -> None:

        @blueprint.route(
            "/sessions/<session_id>/devices/<device_id>/dashboard", methods=["GET"]
        )
        def get_device_dashboard(
            session_id: str, device_id: str
        ) -> ResponseReturnValue:
            try:
                command = GetDeviceEvaluationDetailCommand(
                    session_id=session_id, device_id=device_id
                )
            except ValidationError as e:
                return render_template(
                    "errors/400.html", message=f"Parametri non validi: {e}"
                ), 400
            try:
                device_dashboard = self._get_device_evaluation_detail_use_case.get_device_evaluation_detail(
                    command
                )
            except GetEvaluationDetailFailure as e:
                return render_template(
                    "errors/404.html", message=f"Si è verificato un errore: {e}"
                ), 404
            device_dashboard_dto = DeviceDashboardDTO(
                device_id=device_dashboard.device_id,
                device_name=device_dashboard.name,
                operating_system=device_dashboard.operating_system,
                description=device_dashboard.description,
                aggregate_status=device_dashboard.verdict,
                asset_list=[
                    AssetSummaryDTO(
                        asset_id=a.asset_id,
                        name=a.name,
                        type=a.asset_type,
                        aggregate_status=a.verdict,
                    )
                    for a in device_dashboard.asset_details
                ],
            )
            return render_template(
                "layouts/device/dashboard.html", dashboard=device_dashboard_dto
            ), 200
