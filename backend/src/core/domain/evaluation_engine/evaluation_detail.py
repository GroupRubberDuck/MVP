from dataclasses import dataclass
from types import MappingProxyType

from core.domain.evaluation_object.asset.asset_type import AssetType
from core.domain.evaluation_standard.evaluation_state import EvaluationState
from core.domain.evaluation_standard.decision_tree import Node


@dataclass(frozen=True)
class RequirementEvaluationDetail:
    requirement_id: str
    name: str
    description: str
    target: str
    justification: str
    node_choices: MappingProxyType[str, bool]
    nodes: MappingProxyType[str, Node]
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