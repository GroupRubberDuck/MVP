from flask import Blueprint, request, jsonify
from ....core.ports.inbound.asset.create_asset_use_case import CreateAssetUseCase
from ....core.services.asset.create_asset_command import CreateAssetCommand
from ....core.domain.evaluation_object.asset.asset_type import AssetType

asset_bp = Blueprint("asset", __name__, url_prefix="/api/devices/<string:device_id>/assets")


def create_write_asset_blueprint(service: CreateAssetUseCase) -> Blueprint:

    @asset_bp.post("/")
    def create(device_id: str):
        body = request.get_json()
        command = CreateAssetCommand(
            name=body["name"],
            asset_type=AssetType(body["asset_type"]),
            description=body.get("description", ""),
            session_id=body["session_id"],
        )
        result = service.create_asset(command)
        return jsonify({"success": result}), 201

    return asset_bp