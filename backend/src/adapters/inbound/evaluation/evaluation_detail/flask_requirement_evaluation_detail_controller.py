from adapters.inbound.flask_controller_interface import FlaskController

from core.ports.inbound.asset.get_requirement_evaluation_detail_use_case import (
        GetRequirementEvaluationDetailCommand,
        GetRequirementEvaluationDetailUseCase

)
from core.domain.evaluation_standard.decision_tree import DecisionNode,LeafNode
from core.domain.evaluation_engine.evaluation_detail import (
        RequirementEvaluationDetail
)
from flask import Blueprint, render_template
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
AnyNodeDTO = Annotated[Union[DecisionNodeDTO, LeafNodeDTO], Field(discriminator="node_type")]

# --- Albero e DTO Principale ---

class DecisionTreeDTO(BaseModel):
    root_node_id: str
    nodes: Mapping[str, AnyNodeDTO] # <-- Usiamo l'Annotated Type qui!

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


#controller

class FlaskRequirementEvaluationDetail(FlaskController):
        def __init__(self, _get_requirement_ev_detail_use_case:GetRequirementEvaluationDetailUseCase) -> None:
                self.__get_requirement_ev_detail_use_case=_get_requirement_ev_detail_use_case

        def _make_dto(self, detail: RequirementEvaluationDetail) -> RequirementEvaluationDTO:

                        # 1. Mappatura delle dipendenze
                        deps_dto = tuple(
                                DependencySummaryDTO(id=dep_id, evaluation=dep_state) 
                                for dep_id, dep_state in detail.dependencies
                        )

                        # 2. Creazione della Parent Map
                        parent_map: dict[str, str] = {}
                        for node_id, domain_node in detail.nodes.items():
                                # L'equivalente Python di "domain_node instanceof DecisionNode"
                                        if (yes_child := domain_node.next(True)) is not None: 
                                                parent_map[yes_child] = node_id
                                        if (no_child :=domain_node.next(False)) is not None: 
                                                parent_map[no_child] = node_id      
                        # 3. Mappatura dei Nodi
                        nodes_dto = {}
                        for node_id, domain_node in detail.nodes.items():

                                # ATTENZIONE: Usiamo .get() invece di parent_map[node_id] 
                                # perché per il nodo Root questa chiave non esisterà, e .get() 
                                # restituirà elegantemente None invece di lanciare KeyError.
                                calculated_parent_id = parent_map.get(node_id)

                                if isinstance(domain_node, DecisionNode):  
                                        nodes_dto[node_id] = DecisionNodeDTO(
                                                parent_id=calculated_parent_id,
                                                # Nessun downcast necessario, Python sa che ha .question
                                                question=domain_node.question, 
                                                yes_child_id=domain_node.next(True),
                                                no_child_id=domain_node.next(False)
                                        )
                                elif isinstance(domain_node, LeafNode): 
                                        nodes_dto[node_id] = LeafNodeDTO(
                                                # Ricorda: il domain_node non ha parent_id, 
                                                # dobbiamo usare quello calcolato!
                                                parent_id=calculated_parent_id, 
                                                verdict=domain_node.verdict
                                        )

                        # 4. Creazione dell'Albero Decisionale DTO
                        tree_dto = DecisionTreeDTO(
                                root_node_id=detail.root_id,
                                nodes=nodes_dto
                        )

                        # 5. Assembliamo e ritorniamo il DTO finale
                        return RequirementEvaluationDTO(
                                name=detail.name,
                                norm_description=detail.description,
                                target_description=detail.target,
                                evaluation=detail.state,
                                dependencies=deps_dto,
                                decision_tree=tree_dto,
                                answer=detail.node_choices
                        )     
        
        def register_routes(self, blueprint: Blueprint) -> None:
                        # 1. Aggiunto lo slash mancante
                        @blueprint.route("/session/<session_id>/devices/<device_id>/assets/<asset_id>/requirements/<requirement_id>", methods=["GET"])
                        # Cambiato il nome della funzione per chiarezza
                        def get_requirement_evaluation_detail(session_id:str, device_id:str, asset_id:str, requirement_id:str)-> ResponseReturnValue:
                                
                                try:
                                        command=GetRequirementEvaluationDetailCommand(
                                                        requirement_id=requirement_id,
                                                        asset_id=asset_id,
                                                        device_id=device_id,
                                                        session_id=session_id
                                        )
                                except ValidationError as e:   
                                        return render_template("errors/400.html", message=f"I parametri forniti non sono validi: {e}"), 400
        
                                try:
                                        requirement = self.__get_requirement_ev_detail_use_case.get_evaluation_detail(command)
                                
                                except GetRequirementEvaluationDetailFailure as e: 
                                        return render_template("errors/500.html", message=f"Si è verificato un errore inaspettato: {e}"), 500
        
                                
                                dto = self._make_dto(requirement)
                                return render_template("layouts/requirement_detail.html", requirement=dto), 200
                        
                        