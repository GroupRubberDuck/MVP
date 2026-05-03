# evaluation_result.py
from dataclasses import dataclass, field
from types import MappingProxyType
from core.domain.evaluation_standard.evaluation_state import EvaluationState


@dataclass(frozen=True)
class RequirementResult:
    requirement_id: str
    justification: str
    node_choices: MappingProxyType[str, bool]
    state: EvaluationState
    dependencies: tuple[tuple[str, EvaluationState], ...] = field(
        default_factory=tuple
    )

    def was_blocked_by_dependencies(self) -> bool:
        return any(
            dep_state != EvaluationState.PASS
            for _, dep_state in self.dependencies
        )
    

@dataclass(frozen=True)
class AssetEvaluationResult:
    asset_id: str
    requirement_results: tuple[RequirementResult, ...]
    verdict: EvaluationState

    def get_requirement_result(self, requirement_id: str) -> RequirementResult | None:
        return next((r for r in self.requirement_results
                     if r.requirement_id == requirement_id), None)

    def failed(self) -> tuple[RequirementResult, ...]:
        return tuple(r for r in self.requirement_results
                     if r.state == EvaluationState.FAIL)

    def pending(self) -> tuple[RequirementResult, ...]:
        return tuple(r for r in self.requirement_results
                     if r.state == EvaluationState.PENDING)


@dataclass(frozen=True)
class DeviceEvaluationResult:
    device_id: str
    standard_id: str
    asset_results: tuple[AssetEvaluationResult, ...]
    verdict: EvaluationState

    def get_asset_result(self, asset_id: str) -> AssetEvaluationResult | None:
        return next((a for a in self.asset_results
                     if a.asset_id == asset_id), None)

    def failed_assets(self) -> tuple[AssetEvaluationResult, ...]:
        return tuple(a for a in self.asset_results
                     if a.verdict == EvaluationState.FAIL)

    def pending_assets(self) -> tuple[AssetEvaluationResult, ...]:
        return tuple(a for a in self.asset_results
                     if a.verdict == EvaluationState.PENDING)

    def is_complete(self) -> bool:
        return self.verdict != EvaluationState.PENDING