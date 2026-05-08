from flask import Blueprint, request, send_file, jsonify
from flask.typing import ResponseReturnValue

from adapters.inbound.flask_controller_interface import FlaskController
from core.ports.inbound.device.export_device_use_case import (
    ExportDeviceUseCase,
    ExportDeviceCommand,
)
from core.ports.inbound.device.exceptions import (
    DeviceNotFoundFailure,
    ExportDeviceFailure,
)
from core.domain.evaluation_object.allowed_device_file_extension import AllowedDeviceFileExtension


class ExportDeviceController(FlaskController):

    def __init__(self, export_device_use_case: ExportDeviceUseCase) -> None:
        self._use_case = export_device_use_case

    def register_routes(self, blueprint: Blueprint) -> None:

        @blueprint.route("/api/devices/<device_id>/export", methods=["GET"])
        def export_device(device_id: str) -> ResponseReturnValue:
            extension_param = request.args.get("extension", "json")

            try:
                extension = AllowedDeviceFileExtension(extension_param)
            except ValueError:
                return jsonify({"error": f"Formato non supportato: '{extension_param}'."}), 400

            command = ExportDeviceCommand(
                device_id=device_id,
                extension=extension,
            )

            try:
                exported = self._use_case.export_device(command)
            except DeviceNotFoundFailure as e:
                return jsonify({"error": str(e)}), 404
            except ExportDeviceFailure as e:
                return jsonify({"error": str(e)}), 422

            return send_file(
                exported.content,
                mimetype=exported.media_type,
                download_name=exported.filename,
            )