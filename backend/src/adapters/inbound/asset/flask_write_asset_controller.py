from flask import Blueprint, request, jsonify, render_template
from flask.typing import ResponseReturnValue
from pydantic import ValidationError,BaseModel

from adapters.inbound.flask_controller_interface import FlaskController
from core.ports.inbound.asset.create_asset_use_case import (
    CreateAssetUseCase,
    CreateAssetCommand,
)
from core.ports.inbound.asset.delete_asset_use_case import (
    DeleteAssetUseCase,
    DeleteAssetCommand,
)
from core.ports.inbound.asset.update_asset_use_case import (
    UpdateAssetUseCase,
    UpdateAssetCommand,
)
from core.ports.inbound.asset.exceptions import (
    CreateAssetFailure,
    UpdateAssetFailure,
    DeleteAssetFailure,
)


class FlaskWriteAssetController(FlaskController):

    def __init__(
        self,
        create_asset_use_case: CreateAssetUseCase,
        delete_asset_use_case: DeleteAssetUseCase,
        update_asset_use_case: UpdateAssetUseCase,
    ) -> None:
        self._create_asset_use_case = create_asset_use_case
        self._delete_asset_use_case = delete_asset_use_case
        self._update_asset_use_case = update_asset_use_case

    def register_routes(self, blueprint: Blueprint) -> None:

        @blueprint.route(
            "/api/sessions/<session_id>/devices/<device_id>/assets",
            methods=["POST"],
        )
        def create_asset(session_id: str, device_id: str) -> ResponseReturnValue:
            body = request.get_json(silent=True)
            if body is None:
                return jsonify({"error": "Body JSON mancante o non valido."}), 400

            try:
                command = CreateAssetCommand(
                    session_id=session_id,
                    device_id=device_id,
                    name=body.get("name", ""),
                    asset_type=body.get("asset_type", ""),
                    description=body.get("description", ""),
                )
            except ValidationError as e:
                return jsonify({"error": str(e)}), 400

            try:
                asset_id = self._create_asset_use_case.create_asset(command)
            except CreateAssetFailure as e:
                return jsonify({"error": str(e)}), 400

            return jsonify({"asset_id": asset_id}), 201

        @blueprint.route(
            "/api/sessions/<session_id>/devices/<device_id>/assets/<asset_id>",
            methods=["PUT"],
        )
        def update_asset(session_id: str, device_id: str, asset_id: str) -> ResponseReturnValue:
            body = request.get_json(silent=True)
            if body is None:
                return jsonify({"error": "Body JSON mancante o non valido."}), 400

            try:
                command = UpdateAssetCommand(
                    session_id=session_id,
                    device_id=device_id,
                    asset_id=asset_id,
                    name=body.get("name", ""),
                    asset_type=body.get("asset_type", ""),
                    description=body.get("description", ""),
                )
            except ValidationError as e:
                return jsonify({"error": str(e)}), 400

            try:
                self._update_asset_use_case.update_asset(command)
            except UpdateAssetFailure as e:
                return jsonify({"error": str(e)}), 400

            return "", 204

        @blueprint.route(
            "/api/sessions/<session_id>/devices/<device_id>/assets/<asset_id>",
            methods=["DELETE"],
        )
        def delete_asset(session_id: str, device_id: str, asset_id: str) -> ResponseReturnValue:
            try:
                command = DeleteAssetCommand(
                    session_id=session_id,
                    device_id=device_id,
                    asset_id=asset_id,
                )
            except ValidationError as e:
                return jsonify({"error": str(e)}), 400

            try:
                self._delete_asset_use_case.delete_asset(command)
            except DeleteAssetFailure as e:
                return jsonify({"error": str(e)}), 400

            return "", 204
        


