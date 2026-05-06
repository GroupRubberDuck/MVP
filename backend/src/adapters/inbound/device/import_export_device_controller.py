from flask import Blueprint, jsonify, request
from flask.typing import ResponseReturnValue

from adapters.inbound.flask_controller_interface import FlaskController
from adapters.inbound.utilities.upload_file_controller import UploadFileController

from core.ports.inbound.device.exceptions import (
    DeviceRegistrationFailure,
    ImportDeviceFailure,
)
from core.ports.inbound.device.import_device_use_case import (
    ImportDeviceCommand,
    ImportDeviceUseCase,
)


class ImportDeviceController(FlaskController):

    def __init__(self, import_device_service: ImportDeviceUseCase) -> None:
        self._service = import_device_service

    def register_routes(self, blueprint: Blueprint) -> None:

        @blueprint.route("/api/devices/import", methods=["POST"])
        def import_device() -> ResponseReturnValue:
            if "file" not in request.files:
                return jsonify({"error": "Nessun file presente nella richiesta HTTP."}), 400

            file_storage = request.files["file"]
            if not file_storage.filename:
                return jsonify({"error": "Nessun file selezionato."}), 400

            try:
                extension = UploadFileController.get_http_file_extension(
                    file_storage.filename
                )
            except ValueError as e:
                return jsonify({"error": str(e)}), 400

            file_payload = UploadFileController.get_http_file_payload(file_storage)
            command = ImportDeviceCommand(
                device_file_content=file_payload, extension=extension
            )

            try:
                self._service.import_device(command)
            except ImportDeviceFailure as e:
                return jsonify({"error": str(e)}), 422
            except DeviceRegistrationFailure as e:
                return jsonify({"error": str(e)}), 409

            return jsonify({"message": "Dispositivo importato con successo."}), 201