from flask import Blueprint, request, jsonify
from flask.typing import ResponseReturnValue
from pydantic import ValidationError

from adapters.inbound.flask_controller_interface import FlaskController
from core.ports.inbound.evaluation.evaluate_decision_node_use_case import (
    EvaluateDecisionNodeCommand,
    EvaluateDecisionNodeUseCase
)
from core.ports.inbound.evaluation.exceptions import EvaluateNodeFailure

class FlaskEvaluateDecisionNodeController(FlaskController):
        def __init__(
                self,
                evaluate_decision_node_use_case: EvaluateDecisionNodeUseCase
                ) -> None :
                self._evaluate_decision_node_use_case=evaluate_decision_node_use_case

        def register_routes(self, blueprint: Blueprint) -> None:

                @blueprint.route(
                                "/api/sessions/<session_id>/devices/<device_id>/assets/<asset_id>/requirements/<req_id>",
                                 methods=["PUT"])
                def insert_decision_node_evaluation(
                                session_id:str,
                                device_id:str,
                                asset_id:str,
                                req_id:str
                                )-> ResponseReturnValue:
                        body = request.get_json(silent=True)
                        if body is None:
                            return jsonify({"error": "Body JSON mancante o non valido."}), 400
                        
                        try:
                                command=EvaluateDecisionNodeCommand(
                                        session_id=session_id,
                                        device_id=device_id,
                                        asset_id=asset_id,
                                        requirement_id=req_id,
                                        node_id=body.get("node_id",None),
                                        answer=body.get("answer",None)
                                )
                        except ValidationError as e:
                                return jsonify({"error": str(e)}), 400
                        try:
                                self._evaluate_decision_node_use_case.evaluate_node(
                                        command=command                
                                )
                        except EvaluateNodeFailure as e:
                                return jsonify({"error": str(e)}), 400
                        
                        return jsonify({"message": "valutazione registrata con successo."}), 200