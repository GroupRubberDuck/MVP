from core.domain.evaluation_object.device import Device
from core.domain.evaluation_object.asset import Asset
from core.domain.evaluation_standard.compliance_standard import ComplianceStandard
# from core.domain.evaluation_standard.requirement import Requirement
from core.domain.evaluation_standard.evaluation_state import EvaluationState
from core.domain.evaluation_engine.evaluation_result import (
    RequirementResult,
    AssetEvaluationResult,
    DeviceEvaluationResult,
)
from collections.abc import Sequence
from functools import cache
from types import MappingProxyType
from types import MappingProxyType

class EvaluationEngine:

    def evaluate(self, device: Device,
                 standard: ComplianceStandard) -> DeviceEvaluationResult:
        asset_results = tuple(
            self._evaluate_asset(asset, standard)
            for asset in device.assets.values()
        )
        verdict = self._aggregate_evaluation_states(
            tuple(a.verdict for a in asset_results)
        )
        return DeviceEvaluationResult(
            device_id=device.id,
            standard_id=standard.id,
            asset_results=asset_results,
            verdict=verdict,
        )


    def _evaluate_asset(self, asset: Asset,
                        standard: ComplianceStandard) -> AssetEvaluationResult:
        """Cache subisce side effect, viene usata da _resolve per realizzare la memoizzazione"""
        cache: dict[str, RequirementResult] = {}

        for requirement in standard.requirements:
            self._resolve(requirement.requirement_id, standard, asset, cache)

        requirement_results = tuple(cache.values())
        verdict = self._aggregate_evaluation_states(
            tuple(r.state for r in requirement_results)
        )
        return AssetEvaluationResult(
            asset_id=asset.id,
            requirement_results=requirement_results,
            verdict=verdict,
        )

    def _resolve(self, requirement_id: str,
                 standard: ComplianceStandard,
                 asset: Asset,
                 cache: dict[str, RequirementResult]) -> RequirementResult:
        """Cache subisce side effect, viene usata da _resolve per realizzare la memoizzazione"""
        if requirement_id in cache:
            return cache[requirement_id]

        requirement = standard.get_requirement(requirement_id)
        answer = asset.get_answer(requirement_id)

        dependencies = tuple(
            (dep_id, self._resolve(dep_id, standard, asset, cache).state)
            for dep_id in requirement.dependency_ids
        )

        if answer is None:
            state = EvaluationState.PENDING
        else:
            state = requirement.evaluate(answer, dependencies)

        result = RequirementResult(
            requirement_id=requirement_id,
            justification=answer.justification if answer else "",
            node_choices=answer.node_choices if answer else MappingProxyType({}),
            state=state,
            dependencies=dependencies,
        )
        cache[requirement_id] = result
        return result

    def _aggregate_evaluation_states(self,
                                     states: Sequence[EvaluationState]) -> EvaluationState:
        if any(state == EvaluationState.FAIL for state in states):
            return EvaluationState.FAIL
        if any(state == EvaluationState.PENDING for state in states):
            return EvaluationState.PENDING
        return EvaluationState.PASS