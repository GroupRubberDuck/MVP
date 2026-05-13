from adapters.inbound.flask_controller_interface import FlaskController
from core.ports.inbound.device.create_device_use_case import CreateDeviceUseCase, CreateDeviceCommand
from core.ports.inbound.device.update_device_anagraphic_use_case import UpdateDeviceUseCase, UpdateDeviceCommand
from core.ports.inbound.device.delete_device_use_case import DeleteDeviceUseCase, DeleteDeviceCommand
from core.ports.inbound.device.exceptions import (
    CreateDeviceFailure,
    UpdateDeviceFailure,
    DeleteDeviceFailure
)
from flask import request, jsonify,url_for
from pydantic import ValidationError 

class FlaskWriteDeviceController(FlaskController):
    def __init__(
        self,
        create_device_use_case: CreateDeviceUseCase,
        update_device_use_case: UpdateDeviceUseCase,
        delete_device_use_case: DeleteDeviceUseCase,
    ) -> None:
        self._create_device_use_case = create_device_use_case
        self._update_device_use_case = update_device_use_case
        self._delete_device_use_case = delete_device_use_case

    def register_routes(self, blueprint):
        @blueprint.route("/devices", methods=["POST"])
        def create_device():
            
            data = request.get_json()
            if data is None:
                return jsonify({"error": "Body JSON mancante o non valido."}), 400
            try:
                command = CreateDeviceCommand(**data)
            except ValidationError as e:
                return jsonify({"error": str(e)}), 400
            
            try:
                device_id = self._create_device_use_case.create_device(command)
            except CreateDeviceFailure as e:
                return jsonify({"error": str(e)}), 409

            return jsonify({
                "device_id": device_id,
                "redirect_url":url_for('devices.get_device_detail',device_id=device_id)
                }), 201

        @blueprint.route("/devices/<device_id>", methods=["PUT"])
        def update_device(device_id):
            data = request.get_json()
            if data is None:
                    return jsonify({"error": "Body JSON mancante o non valido."}), 400
            
            try:
                command = UpdateDeviceCommand(device_id=device_id, **data)
            except ValidationError as e:
                return jsonify({"error": str(e)}), 400

            try:
                self._update_device_use_case.update_device(command)
            except UpdateDeviceFailure as e:
                return jsonify({"error": str(e)}), 404
            return jsonify({
                "redirect_url": url_for("devices.get_device_detail", device_id=device_id)
            }), 200

        @blueprint.route("/devices/<device_id>", methods=["DELETE"])
        def delete_device(device_id):
            try:
                command = DeleteDeviceCommand(device_id=device_id)
            except ValidationError as e:
                return jsonify({"error": str(e)}), 400
            
            try:
                self._delete_device_use_case.delete_device(command)
            except DeleteDeviceFailure as e:
                return jsonify({"error": str(e)}), 404
            
            return "", 204

