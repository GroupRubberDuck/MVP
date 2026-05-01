# evaluation_engine.py
from types import MappingProxyType

from core.domain.evaluation_object.device import Device
from core.domain.evaluation_object.asset import Asset
from core.domain.evaluation_object.answer import Answer
from core.domain.evaluation_standard.compliance_standard import ComplianceStandard
from core.domain.evaluation_standard.requirement import Requirement
from core.domain.evaluation_standard.evaluation_state import EvaluationState
from core.domain.evaluation_engine.evaluation_result import (
    RequirementResult,
    AssetEvaluationResult,
    DeviceEvaluationResult,
)


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
            device_name=device.name,
            device_os=device.os,
            standard_id=standard.id,
            standard_name=standard.name,
            standard_version=standard.version_number,
            asset_results=asset_results,
            verdict=verdict,
        )

    def _evaluate_asset(self, asset: Asset,
                        standard: ComplianceStandard) -> AssetEvaluationResult:
        # Cache condivisa per tutta la valutazione dell'asset.
        # _resolve garantisce che ogni requisito venga calcolato una sola volta
        # e che le dipendenze vengano risolte ricorsivamente prima del requisito
        # che le referenzia, indipendentemente dall'ordine nello standard.
        cache: dict[str, RequirementResult] = {}

        for requirement in standard.requirements:
            self._resolve(requirement.requirement_id, standard, asset, cache)

        requirement_results = tuple(cache.values())
        verdict = self._aggregate_evaluation_states(
            tuple(r.state for r in requirement_results)
        )
        return AssetEvaluationResult(
            asset_id=asset.id,
            asset_name=asset.name,
            asset_type=asset.asset_type,
            requirement_results=requirement_results,
            verdict=verdict,
        )

    def _resolve(self, requirement_id: str,
                 standard: ComplianceStandard,
                 asset: Asset,
                 cache: dict[str, RequirementResult]) -> RequirementResult:
        """
        Restituisce il RequirementResult per requirement_id, calcolandolo
        ricorsivamente se non è ancora in cache. Garantisce che le dipendenze
        siano sempre risolte prima del requisito che le referenzia.
        """
        if requirement_id in cache:
            return cache[requirement_id]

        requirement = standard.get_requirement(requirement_id)
        answer = asset.answers.get(requirement_id)

        # Prima risolve ricorsivamente tutte le dipendenze,
        # poi costruisce la tupla con i loro stati.
        dependencies = tuple(
            (dep_id, self._resolve(dep_id, standard, asset, cache).state)
            for dep_id in requirement.dependency_ids
        )

        result = self._evaluate_requirement(requirement, answer, dependencies)
        cache[requirement_id] = result
        return result

    def _evaluate_requirement(self, requirement: Requirement,
                               answer: Answer | None,
                               dependencies: tuple[tuple[str, EvaluationState], ...] | None = None
                               ) -> RequirementResult:
        if dependencies is None:
            dependencies = ()
        blocked_state = self._check_dependencies(dependencies)
        if blocked_state is not None:
            return RequirementResult(
                requirement_id=requirement.requirement_id,
                requirement_name=requirement.name,
                description=requirement.description,
                target_description=requirement.target_description,
                justification=answer.justification if answer else "",
                node_choices=answer.node_choices if answer else MappingProxyType({}),
                state=blocked_state,
                dependencies=dependencies,
            )

        if answer is None:
            return RequirementResult(
                requirement_id=requirement.requirement_id,
                requirement_name=requirement.name,
                description=requirement.description,
                target_description=requirement.target_description,
                justification="",
                node_choices=MappingProxyType({}),
                state=EvaluationState.PENDING,
                dependencies=dependencies,
            )

        state = requirement.evaluate(answer.node_choices)
        return RequirementResult(
            requirement_id=requirement.requirement_id,
            requirement_name=requirement.name,
            description=requirement.description,
            target_description=requirement.target_description,
            justification=answer.justification,
            node_choices=answer.node_choices,
            state=state,
            dependencies=dependencies,
        )

    def _check_dependencies(self,
                            dependencies: tuple[tuple[str, EvaluationState], ...]
                            ) -> EvaluationState | None:
        """
        Restituisce lo stato bloccante se almeno una dipendenza non è PASS,
        altrimenti None. Priorità: FAIL > PENDING > NA.
        """
        if not dependencies:
            return None

        states = {dep_state for _, dep_state in dependencies}

        if EvaluationState.FAIL in states:
            return EvaluationState.FAIL
        if EvaluationState.PENDING in states:
            return EvaluationState.PENDING
        if EvaluationState.NA in states:
            return EvaluationState.NA

        return None

    def _aggregate_evaluation_states(self,
                                     states: tuple[EvaluationState, ...]) -> EvaluationState:
        if any(state == EvaluationState.FAIL for state in states):
            return EvaluationState.FAIL
        if any(state == EvaluationState.PENDING for state in states):
            return EvaluationState.PENDING
        return EvaluationState.PASS