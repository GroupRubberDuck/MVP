from flask import Blueprint, Request, Response, request, jsonify
 
from core.ports.inbound.evaluation.evaluation_session.insert_justification_use_case import InsertJustificationUseCase
from core.services.evaluation.insert_justification_command import InsertJustificationCommand
 
evaluation_justification_blueprint = Blueprint("evaluation_justification", __name__)
 
 
class EvaluationJustificationController:
 
    def __init__(self, insert_justification_use_case: InsertJustificationUseCase) -> None:
        self._use_case = insert_justification_use_case
        self._register_routes()
 
    def _register_routes(self) -> None:
        evaluation_justification_blueprint.add_url_rule(
            "/sessions/<session_id>/assets/<asset_id>/requirements/<requirement_id>/nodes/<node_id>/justification",
            view_func=self.insert_justification,
            methods=["PUT"],
        )
 
    def insert_justification(
        self,
        session_id: str,
        asset_id: str,
        requirement_id: str,
        node_id: str,
    ) -> Response:
        body = request.get_json(silent=True) or {}
        justification = body.get("justification", "")
 
        command = InsertJustificationCommand(
            session_id=session_id,
            asset_id=asset_id,
            requirement_id=requirement_id,
            node_id=node_id,
            justification=justification,
        )
 
        self._use_case.insert_justification(command)
 
        return jsonify({"message": "Justification inserted successfully"}), 200