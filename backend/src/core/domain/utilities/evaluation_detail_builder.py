from core.domain.evaluation_engine.evaluation_detail import (
    NodeDetail,
    RequirementEvaluationDetail,
    AssetEvaluationDetail,
    DeviceEvaluationDetail,
)

from core.domain.evaluation_engine.evaluation_result import (
    DeviceEvaluationResult,
    AssetEvaluationResult,
    RequirementEvaluationResult,
)

from core.domain.evaluation_object.device import Device
from core.domain.evaluation_standard.compliance_standard import ComplianceStandard
from core.domain.evaluation_standard.requirement import Requirement
from core.domain.evaluation_standard.decision_tree import Node, DecisionNode, LeafNode

from types import MappingProxyType
from collections.abc import Mapping


class EvaluationDetailBuilder:
    def build_device_detail(
        self,
        result: DeviceEvaluationResult,
        device: Device,
        standard: ComplianceStandard,
    ) -> DeviceEvaluationDetail:
        asset_details = tuple(
            self.build_asset_detail(ar, device, standard) for ar in result.asset_results
        )
        return DeviceEvaluationDetail(
            device_id=device.id,
            name=device.name,
            operating_system=device.os,
            description=device.description,
            standard_id=standard.id,
            asset_details=asset_details,
            verdict=result.verdict,
        )

    def build_asset_detail(
        self,
        result: AssetEvaluationResult,
        device: Device,
        standard: ComplianceStandard,
    ) -> AssetEvaluationDetail:
        asset = device.get_asset(result.asset_id)
        requirement_details = tuple(
            self.build_requirement_detail(
                rr, standard.get_requirement(rr.requirement_id)
            )
            for rr in result.requirement_results
        )
        return AssetEvaluationDetail(
            asset_id=asset.id,
            name=asset.anagraphic.name,
            asset_type=asset.anagraphic.asset_type,
            description=asset.anagraphic.description,
            requirement_details=requirement_details,
            verdict=result.verdict,
        )

    def build_requirement_detail(
        self,
        result: RequirementEvaluationResult,
        req: Requirement,
    ) -> RequirementEvaluationDetail:
        if req.decision_tree is None:
            return RequirementEvaluationDetail(
                requirement_id=result.requirement_id,
                name=req.name,
                description=req.description,
                target=req.target_description,
                justification=result.justification,
                root_id="",
                node_choices=result.node_choices,
                nodes=MappingProxyType({}),
                state=result.state,
                dependencies=result.dependencies,
            )

        node_details = self._make_nodes_detail(req.decision_tree.nodes)

        return RequirementEvaluationDetail(
            requirement_id=result.requirement_id,
            name=req.name,
            description=req.description,
            target=req.target_description,
            justification=result.justification,
            root_id=req.decision_tree.root_id,
            node_choices=result.node_choices,
            nodes=MappingProxyType(node_details),
            state=result.state,
            dependencies=result.dependencies,
        )

    def _make_nodes_detail(self, nodes: Mapping[str, Node]) -> dict[str, NodeDetail]:
        parent_map: dict[str, str] = {}
        for node_id, node in nodes.items():
            if isinstance(node, DecisionNode):
                child_true = node.next(True)
                child_false = node.next(False)
                if child_true is not None:
                    parent_map[child_true] = node_id
                if child_false is not None:
                    parent_map[child_false] = node_id

        result: dict[str, NodeDetail] = {}
        for node_id, node in nodes.items():
            parent_id = parent_map.get(node_id)

            if isinstance(node, DecisionNode):
                result[node_id] = NodeDetail(
                    node_id=node_id,
                    node_type="decision",
                    question=node.question,
                    child_on_true_id=node.next(True),
                    child_on_false_id=node.next(False),
                    verdict=None,
                    parent_id=parent_id,
                )
            elif isinstance(node, LeafNode):
                result[node_id] = NodeDetail(
                    node_id=node_id,
                    node_type="leaf",
                    question=None,
                    child_on_true_id=None,
                    child_on_false_id=None,
                    verdict=node.verdict,
                    parent_id=parent_id,
                )

        return result
