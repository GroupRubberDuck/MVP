from dataclasses import dataclass
from types import MappingProxyType
from collections.abc import Mapping
from core.domain.evaluation_object.asset.asset_type import AssetType
from core.domain.evaluation_standard.evaluation_state import EvaluationState
from core.domain.evaluation_standard.standard_verdict import StandardVerdict


@dataclass(frozen=True)
class NodeDetail:
    node_id: str
    node_type: str  # "decision" | "leaf"
    question: str | None  # solo per decision
    child_on_true_id: str | None  # solo per decision
    child_on_false_id: str | None  # solo per decision
    verdict: StandardVerdict | None  # solo per leaf
    parent_id: str | None


@dataclass(frozen=True)
class RequirementEvaluationDetail:
    requirement_id: str
    name: str
    description: str
    target: str
    justification: str
    root_id: str
    node_choices: MappingProxyType[str, bool]
    nodes: Mapping[str, NodeDetail]
    state: EvaluationState
    dependencies: tuple[tuple[str, EvaluationState], ...]


@dataclass(frozen=True)
class AssetEvaluationDetail:
    asset_id: str
    name: str
    asset_type: AssetType
    description: str
    requirement_details: tuple[RequirementEvaluationDetail, ...]
    verdict: EvaluationState


@dataclass(frozen=True)
class DeviceEvaluationDetail:
    device_id: str
    name: str
    operating_system: str
    description: str
    standard_id: str
    asset_details: tuple[AssetEvaluationDetail, ...]
    verdict: EvaluationState
