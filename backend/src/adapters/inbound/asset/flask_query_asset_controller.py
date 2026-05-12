from flask import Blueprint, request, jsonify, render_template
from flask.typing import ResponseReturnValue
from pydantic import ValidationError,BaseModel

from adapters.inbound.flask_controller_interface import FlaskController

from core.ports.inbound.asset.get_asset_anagraphic_use_case import GetAssetAnagraphicUseCase, GetAssetAnagraphicCommand


class AssetAnagraphicDTO(BaseModel):
    asset_id:str
    asset_name:str | None
    asset_type:str | None
    asset_description: str | None

class FlaskQueryAssetController(FlaskController):

    def __init__(
        self,
        get_asset_anagraphic_use_case: GetAssetAnagraphicUseCase 
    ) -> None:
        self._get_asset_anagraphic_use_case = get_asset_anagraphic_use_case

    def register_routes(self, blueprint: Blueprint) -> None:

        @blueprint.route("/sessions/<session_id>/devices/<device_id>/assets", methods=["GET"])
        def create_asset_page(session_id: str, device_id: str): 
            return render_template(
                "asset/create_asset.html",
                session_id=session_id,
                device_id=device_id,
                asset=None
            ), 200

        @blueprint.route("/sessions/<session_id>/devices/<device_id>/assets/<asset_id>/edit", methods=["GET"])
        def edit_asset_page(session_id: str, device_id: str, asset_id: str):
            
            command=GetAssetAnagraphicCommand(
                device_id=device_id,
                session_id=session_id,
                asset_id=asset_id
            )

            asset_anagraphic=self._get_asset_anagraphic_use_case.get_asset_anagraphic(
                command=command
            )

            asset_dto=AssetAnagraphicDTO(
                asset_description=asset_anagraphic.description,
                asset_id=asset_id,
                asset_name=asset_anagraphic.name,
                asset_type=asset_anagraphic.asset_type
            )
            
            return render_template(
                "asset/create_asset.html",
                session_id=session_id,
                device_id=device_id,
                asset=asset_dto
            ), 200

   