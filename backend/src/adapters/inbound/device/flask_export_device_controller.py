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


class FlaskExportDeviceController(FlaskController):

    def __init__(self, export_device_use_case: ExportDeviceUseCase) -> None:
        self._use_case = export_device_use_case

    def register_routes(self, blueprint: Blueprint) -> None:

        @blueprint.route("/api/devices/<device_id>/export", methods=["GET"])
        def export_device(device_id: str) -> ResponseReturnValue:
            extension_raw = request.args.get("extension", "json")
            extension_param = extension_raw.lower()

            try:
                extension = AllowedDeviceFileExtension(extension_param)
            except ValueError:
                return jsonify({"error": f"Formato non supportato: '{extension_raw}'."}), 400
            command = ExportDeviceCommand(
                device_id=device_id,
                extension=extension,
            )

            try:
                exported = self._use_case.export_device(command)
                return send_file(
                    exported.content,
                    mimetype=exported.media_type,
                    as_attachment=True,
                    download_name=exported.filename
                )

            except DeviceNotFoundFailure as e:
                return jsonify({"error": str(e)}), 404
            except ExportDeviceFailure as e:
                return jsonify({"error": str(e)}), 422
            except Exception as e:
                import traceback
                traceback.print_exc()
                return jsonify({"error": f"Errore interno del server: {str(e)}"}), 500