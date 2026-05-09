from core.ports.inbound.device.get_device_list_use_case import GetDeviceListUseCase
from core.ports.inbound.device.get_device_use_case import GetDeviceDetailCommand, GetDeviceDetailUseCase
from core.ports.inbound.compliance_standard.get_compliance_standard_use_case import GetComplianceStandardCommand, GetComplianceStandardUseCase
from core.ports.inbound.compliance_standard.exceptions import StandardNotFoundFailure
from core.ports.inbound.device.exceptions import DeviceNotFoundFailure
from adapters.inbound.flask_controller_interface import FlaskController
from flask import Blueprint, render_template
from pydantic import BaseModel


class DeviceListItemDTO(BaseModel):
    device_id: str
    name: str


class DeviceDetailDTO(BaseModel):
    device_id: str
    name: str
    os: str
    description: str
    compliance_standard_name: str
    compliance_standard_version: str


class FlaskQueryDeviceController(FlaskController):
    def __init__(
        self,
        get_device_list_use_case: GetDeviceListUseCase,
        get_device_detail_use_case: GetDeviceDetailUseCase,
        get_compliance_standard_use_case: GetComplianceStandardUseCase,
    ) -> None:
        self._get_device_list_use_case = get_device_list_use_case
        self._get_device_detail_use_case = get_device_detail_use_case
        self._get_compliance_standard_use_case = get_compliance_standard_use_case

    def register_routes(self, blueprint: Blueprint) -> None:

        @blueprint.route("/devices", methods=["GET"])
        def get_device_list():
            device_list = self._get_device_list_use_case.get_device_list()
            device_list_dto = [
                DeviceListItemDTO(
                    device_id=d.device_id,
                    name=d.name,
                )
                for d in device_list
            ]
            return render_template("layouts/device/device_list.html", devices=device_list_dto)

        @blueprint.route("/devices/<device_id>", methods=["GET"])
        def get_device_detail(device_id):
            command = GetDeviceDetailCommand(device_id=device_id)
            try:
                device = self._get_device_detail_use_case.get_device_detail(command)
                standard = self._get_compliance_standard_use_case.get_compliance_standard(
                    GetComplianceStandardCommand(standard_id=device.standard_id)
                )
                return render_template(
                    "layouts/device/device_detail.html",
                    device=DeviceDetailDTO(
                        device_id=device.id,
                        name=device.name,
                        os=device.os,
                        description=device.description,
                        compliance_standard_name=standard.name,
                        compliance_standard_version=standard.version_number,
                    ),
                ), 200
            except DeviceNotFoundFailure as e:
                return render_template("errors/404.html", message=str(e)), 404
            except StandardNotFoundFailure as e:
                return render_template("errors/404.html", message=str(e)), 404
            
        @blueprint.route("/devices/<device_id>/edit", methods=["GET"])
        def edit_device_page(device_id):
            command = GetDeviceDetailCommand(device_id=device_id)
            try:
                device = self._get_device_detail_use_case.get_device_detail(command)
            except DeviceNotFoundFailure as e:
                return render_template("errors/404.html", message=str(e)), 404
            
            return render_template("layouts/device/edit_device.html", device=DeviceDetailDTO(
                    device_id=device.id,
                    name=device.name,
                    os=device.os,
                    description=device.description,
                    compliance_standard_name="",  # Non necessario per la pagina di modifica
                    compliance_standard_version=""  # Non necessario per la pagina di modifica
                )), 200
        
        @blueprint.route("/devices/create", methods=["GET"])
        def create_device_page():
            return render_template("layouts/device/create_device.html")