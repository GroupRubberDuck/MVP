from adapters.inbound.flask_controller_interface import FlaskController

from core.ports.inbound.asset.get_requirement_evaluation_detail_use_case import (
    GetRequirementEvaluationDetailCommand,
    GetRequirementEvaluationDetailUseCase,
)
from core.domain.evaluation_engine.evaluation_detail import (
    RequirementEvaluationDetail,
    NodeDetail,
)
from flask import Blueprint, render_template, jsonify
from flask.typing import ResponseReturnValue

from core.domain.evaluation_engine.evaluation_result import EvaluationState
from core.domain.evaluation_standard.standard_verdict import StandardVerdict

from core.ports.inbound.asset.exceptions import GetRequirementEvaluationDetailFailure
from typing import Annotated, Literal, Union
from pydantic import BaseModel, Field, ValidationError
from collections.abc import Mapping
# DTOs

# --- Nodi ---


class NodeBaseDTO(BaseModel):
    parent_id: str | None
    # Potresti voler aggiungere configurazioni qui, se necessario


class DecisionNodeDTO(NodeBaseDTO):
    # Il frontend userà questo campo per fare un if/switch
    node_type: Literal["decision"] = "decision"
    question: str
    yes_child_id: str | None
    no_child_id: str | None


class LeafNodeDTO(NodeBaseDTO):
    node_type: Literal["leaf"] = "leaf"
    verdict: StandardVerdict


# Creiamo un tipo che dice a Pydantic:
# "Guarda il campo 'node_type' per capire quale classe usare"
AnyNodeDTO = Annotated[
    Union[DecisionNodeDTO, LeafNodeDTO], Field(discriminator="node_type")
]

# --- Albero e DTO Principale ---


class DecisionTreeDTO(BaseModel):
    root_node_id: str
    nodes: Mapping[str, AnyNodeDTO]


class DependencySummaryDTO(BaseModel):
    id: str
    evaluation: EvaluationState


class RequirementEvaluationDTO(BaseModel):
    name: str
    norm_description: str
    target_description: str
    evaluation: EvaluationState
    dependencies: tuple[DependencySummaryDTO, ...]
    decision_tree: DecisionTreeDTO
    answer: Mapping[str, bool]
    justification: str | None


# controller


class FlaskRequirementEvaluationDetailController(FlaskController):
    def __init__(
        self, get_requirement_ev_detail_use_case: GetRequirementEvaluationDetailUseCase
    ) -> None:
        self._get_requirement_ev_detail_use_case = get_requirement_ev_detail_use_case

    def _make_node_dto(self, node: NodeDetail) -> AnyNodeDTO:
        if node.node_type == "decision":
            return DecisionNodeDTO(
                parent_id=node.parent_id,
                question=node.question or "",
                yes_child_id=node.child_on_true_id,
                no_child_id=node.child_on_false_id,
            )
        if node.node_type == "leaf":
            return LeafNodeDTO(
                parent_id=node.parent_id,
                verdict=node.verdict,  # type: ignore[arg-type]
            )
        raise ValueError(f"Tipo di nodo sconosciuto: {node.node_type}")

    def _make_dto(
        self, detail: RequirementEvaluationDetail
    ) -> RequirementEvaluationDTO:
        nodes_dto = {
            node_id: self._make_node_dto(node) for node_id, node in detail.nodes.items()
        }

        return RequirementEvaluationDTO(
            name=detail.name,
            norm_description=detail.description,
            target_description=detail.target,
            evaluation=detail.state,
            dependencies=tuple(
                DependencySummaryDTO(id=dep_id, evaluation=dep_state)
                for dep_id, dep_state in detail.dependencies
            ),
            answer=detail.node_choices,
            decision_tree=DecisionTreeDTO(
                root_node_id=detail.root_id,
                nodes=nodes_dto,
            ),
            justification=detail.justification,
        )

    def register_routes(self, blueprint: Blueprint) -> None:

        @blueprint.route(
            "/sessions/<session_id>/devices/<device_id>/assets/<asset_id>/requirements/<requirement_id>",
            methods=["GET"],
        )
        def get_requirement_evaluation_detail(
            session_id: str,
            device_id: str,
            asset_id: str,
            requirement_id: str,
        ) -> ResponseReturnValue:
            try:
                command = GetRequirementEvaluationDetailCommand(
                    requirement_id=requirement_id,
                    asset_id=asset_id,
                    device_id=device_id,
                    session_id=session_id,
                )
            except ValidationError as e:
                return render_template(
                    "errors/400.html",
                    message=f"I parametri forniti non sono validi: {e}",
                ), 400

            try:
                detail = self._get_requirement_ev_detail_use_case.get_evaluation_detail(
                    command
                )
            except GetRequirementEvaluationDetailFailure as e:
                return render_template(
                    "errors/404.html",
                    message=f"Risorsa non trovata: {e}",
                ), 404

            dto = self._make_dto(detail)
            return render_template(
                "layouts/requirement_detail.html",
                requirement=dto.model_dump(),
                session_id=session_id,
                device_id=device_id,
                asset_id=asset_id,
                requirement_id=requirement_id,
            ), 200

        @blueprint.route(
            "/api/sessions/<session_id>/devices/<device_id>/assets/<asset_id>/requirements/<requirement_id>",
            methods=["GET"],
        )
        def get_requirement_evaluation_json(
            session_id: str,
            device_id: str,
            asset_id: str,
            requirement_id: str,
        ) -> ResponseReturnValue:
            try:
                command = GetRequirementEvaluationDetailCommand(
                    requirement_id=requirement_id,
                    asset_id=asset_id,
                    device_id=device_id,
                    session_id=session_id,
                )
            except ValidationError as e:
                return render_template(
                    "errors/400.html",
                    message=f"I parametri forniti non sono validi: {e}",
                ), 400

            try:
                detail = self._get_requirement_ev_detail_use_case.get_evaluation_detail(
                    command
                )
            except GetRequirementEvaluationDetailFailure as e:
                return render_template(
                    "errors/404.html",
                    message=f"Risorsa non trovata: {e}",
                ), 404

            dto = self._make_dto(detail)
            return jsonify(dto.model_dump(mode="json")), 200

        @blueprint.route(
            "/api/sessions/<session_id>/devices/<device_id>/assets/<asset_id>/requirements/<requirement_id>/state",
            methods=["GET"],
        )
        def get_requirement_evaluation_state(
            session_id: str,
            device_id: str,
            asset_id: str,
            requirement_id: str,
        ) -> ResponseReturnValue:
            try:
                command = GetRequirementEvaluationDetailCommand(
                    requirement_id=requirement_id,
                    asset_id=asset_id,
                    device_id=device_id,
                    session_id=session_id,
                )
            except ValidationError as e:
                return render_template(
                    "errors/400.html",
                    message=f"I parametri forniti non sono validi: {e}",
                ), 400

            try:
                detail = self._get_requirement_ev_detail_use_case.get_evaluation_detail(
                    command
                )
            except GetRequirementEvaluationDetailFailure as e:
                return render_template(
                    "errors/404.html",
                    message=f"Risorsa non trovata: {e}",
                ), 404

            return jsonify({"evaluation": detail.state}), 200
