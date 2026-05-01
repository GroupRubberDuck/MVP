# evaluation_result.py
from dataclasses import dataclass, field
from types import MappingProxyType
from core.domain.evaluation_standard.evaluation_state import EvaluationState
from ..evaluation_object.asset_type import AssetType


@dataclass(frozen=True)
class RequirementResult:
    # dati anagrafici del requisito
    requirement_id: str
    requirement_name: str
    description: str
    target_description: str
    # risposta dell'utente
    justification: str
    node_choices: MappingProxyType[str, bool]
    # esito
    state: EvaluationState
    # dipendenze: (requirement_id, stato_della_dipendenza_al_momento_della_valutazione)
    dependencies: tuple[tuple[str, EvaluationState], ...] = field(default_factory=tuple)

    def was_blocked_by_dependencies(self) -> bool:
        """True se il requisito non è stato valutato a causa delle dipendenze."""
        return any(dep_state != EvaluationState.PASS for _, dep_state in self.dependencies)


@dataclass(frozen=True)
class AssetEvaluationResult:
    # dati anagrafici dell'asset
    asset_id: str
    asset_name: str
    asset_type: AssetType
    # risultati dei requisiti
    requirement_results: tuple[RequirementResult, ...]
    # esito aggregato
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
    # dati anagrafici del device
    device_id: str
    device_name: str
    device_os: str
    # dati anagrafici dello standard
    standard_id: str
    standard_name: str
    standard_version: str
    # risultati degli asset
    asset_results: tuple[AssetEvaluationResult, ...]
    # esito aggregato
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