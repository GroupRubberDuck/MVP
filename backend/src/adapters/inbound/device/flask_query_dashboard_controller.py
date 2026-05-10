from core.ports.inbound.device.get_device_dashboard_use_case import GetDeviceDashboardUseCase, GetDeviceDashboardCommand
from adapters.inbound.flask_controller_interface import FlaskController
from flask import Blueprint,render_template
from flask.typing import ResponseReturnValue
from core.domain.evaluation_standard.evaluation_state import EvaluationState
from core.domain.evaluation_object.asset.asset_type import AssetType
from pydantic import BaseModel


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
        get_device_dashboard_use_case: GetDeviceDashboardUseCase,
    ) -> None:
        self._get_device_dashboard_use_case = get_device_dashboard_use_case

    def register_routes(self, blueprint: Blueprint) -> None:

        @blueprint.route("/devices/<device_id>/dashboard", methods=["GET"])
        def get_device_list(device_id: str) -> ResponseReturnValue:
            command = GetDeviceDashboardCommand(device_id=device_id)
            device_dashboard = self._get_device_dashboard_use_case.get_device_dashboard(command)
            device_dashboard_dto = DeviceDashboardDTO(
                device_id=device_dashboard.device_id,
                device_name=device_dashboard.device_name,
                operating_system=device_dashboard.operating_system,
                description=device_dashboard.description,
                aggregate_status=device_dashboard.aggregate_status,
                asset_list=[
                    AssetSummaryDTO(
                        asset_id=a.asset_id,
                        name=a.name,
                        type=a.type,
                        aggregate_status=a.aggregate_status
                    ) for a in device_dashboard.asset_list
                ]
            )
            return render_template("layouts/device/dashboard.html", dashboard=device_dashboard_dto)