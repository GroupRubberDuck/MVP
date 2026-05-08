<<<<<<< HEAD
from flask import Blueprint, Response, request, jsonify
 
from core.ports.inbound.evaluation.evaluation_session.insert_justification_use_case import InsertJustificationUseCase
from core.services.evaluation.insert_justification_command import InsertJustificationCommand
 
evaluation_justification_blueprint = Blueprint("evaluation_justification", __name__)
 
 
class EvaluationJustificationController:
 
=======
from flask import Blueprint, request, jsonify
from flask.typing import ResponseReturnValue
from pydantic import ValidationError

from adapters.inbound.flask_controller_interface import FlaskController
from core.ports.inbound.evaluation.evaluation_session.insert_justification_use_case import (
    InsertJustificationUseCase,
    InsertJustificationCommand,
)
from core.ports.inbound.evaluation.exceptions import InsertJustificationFailure


class EvaluationJustificationController(FlaskController):

>>>>>>> 557ff01a2ed040eb76cb77f4dd612be8fb66dfd7
    def __init__(self, insert_justification_use_case: InsertJustificationUseCase) -> None:
        self._use_case = insert_justification_use_case

    def register_routes(self, blueprint: Blueprint) -> None:

        @blueprint.route(
            "/sessions/<session_id>/assets/<asset_id>/requirements/<requirement_id>/justification",
            methods=["PUT"],
        )
        def insert_justification(
            session_id: str,
            asset_id: str,
            requirement_id: str,
        ) -> ResponseReturnValue:
            body = request.get_json(silent=True)
            if body is None:
                return jsonify({"error": "Body JSON mancante o non valido."}), 400

            try:
                command = InsertJustificationCommand(
                    session_id=session_id,
                    asset_id=asset_id,
                    requirement_id=requirement_id,
                    justification=body.get("justification", ""),
                )
            except ValidationError as e:
                return jsonify({"error": str(e)}), 400

            try:
                self._use_case.insert_justification(command)
            except InsertJustificationFailure as e:
                return jsonify({"error": str(e)}), 400

            return jsonify({"message": "Giustificazione inserita con successo."}), 200