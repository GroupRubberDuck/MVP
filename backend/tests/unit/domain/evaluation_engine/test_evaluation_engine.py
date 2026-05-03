import pytest
from unittest.mock import Mock
from types import MappingProxyType

from core.domain.evaluation_engine.evaluation_engine import EvaluationEngine
from core.domain.evaluation_standard.evaluation_state import EvaluationState
from core.domain.evaluation_engine.evaluation_result import (
    RequirementResult,
    AssetEvaluationResult,
    DeviceEvaluationResult,
)


# ── Fixtures ──

@pytest.fixture
def engine() -> EvaluationEngine:
    return EvaluationEngine()


# ── 1. Test Aggregazione Stati ──

class TestAggregateEvaluationStates:

    def test_all_pass_returns_pass(self, engine):
        states = [EvaluationState.PASS, EvaluationState.PASS]
        assert engine._aggregate_evaluation_states(states) == EvaluationState.PASS

    def test_any_fail_returns_fail(self, engine):
        states = [EvaluationState.PASS, EvaluationState.FAIL, EvaluationState.PENDING]
        assert engine._aggregate_evaluation_states(states) == EvaluationState.FAIL

    def test_any_pending_without_fail_returns_pending(self, engine):
        states = [EvaluationState.PASS, EvaluationState.PENDING, EvaluationState.PASS]
        assert engine._aggregate_evaluation_states(states) == EvaluationState.PENDING


# ── 2. Test Risoluzione Requisiti e Dipendenze (_resolve) ──

class TestEvaluationEngineResolve:

    def test_resolve_missing_answer_returns_pending(self, engine):
        """Se manca la risposta, il requisito va in PENDING e viene salvato in cache."""
        mock_standard = Mock()
        mock_req = Mock()
        mock_req.dependency_ids = ()
        mock_standard.get_requirement.return_value = mock_req
        
        mock_asset = Mock()
        mock_asset.get_answer.return_value = None 
        
        cache = {}
        result = engine._resolve("REQ-001", mock_standard, mock_asset, cache)

        assert result.requirement_id == "REQ-001"
        assert result.state == EvaluationState.PENDING
        assert "REQ-001" in cache

    def test_resolve_uses_cache(self, engine):
        """Se il requisito è già nella cache, _resolve lo restituisce senza ricalcolarlo."""
        cached_result = RequirementResult(
            requirement_id="REQ-001", justification="",
            node_choices=MappingProxyType({}), state=EvaluationState.PASS
        )
        cache = {"REQ-001": cached_result}
        
        mock_standard = Mock()
        mock_asset = Mock()
        
        result = engine._resolve("REQ-001", mock_standard, mock_asset, cache)
        
        assert result is cached_result
        mock_standard.get_requirement.assert_not_called()

    def test_resolve_evaluates_dependencies_first(self, engine):
        """Le dipendenze vengono valutate prima del requisito principale."""
        req1 = Mock()
        req1.dependency_ids = ("REQ-002",)
        req1.evaluate.return_value = EvaluationState.PASS
        
        req2 = Mock()
        req2.dependency_ids = ()
        req2.evaluate.return_value = EvaluationState.FAIL
        
        mock_standard = Mock()
        mock_standard.get_requirement.side_effect = lambda r_id: req1 if r_id == "REQ-001" else req2
        
        mock_ans1 = Mock(justification="J1", node_choices=MappingProxyType({}))
        mock_ans2 = Mock(justification="J2", node_choices=MappingProxyType({}))
        
        mock_asset = Mock()
        mock_asset.get_answer.side_effect = lambda r_id: mock_ans1 if r_id == "REQ-001" else mock_ans2
        
        cache = {}
        engine._resolve("REQ-001", mock_standard, mock_asset, cache)

        # Entrambi i requisiti devono essere finiti in cache
        assert cache["REQ-002"].state == EvaluationState.FAIL
        assert cache["REQ-001"].state == EvaluationState.PASS
        
        # Il requisito principale riceve lo stato della dipendenza fallita
        req1.evaluate.assert_called_once_with(mock_ans1, (("REQ-002", EvaluationState.FAIL),))


# ── 3. Test Valutazione Asset (_evaluate_asset) ──

class TestEvaluationEngineEvaluateAsset:

    def test_evaluate_asset_aggregates_all_requirements(self, engine):
        """Verifica che _evaluate_asset iteri sui requisiti e assembli i risultati usando la cache."""
        req1, req2 = Mock(), Mock()
        req1.requirement_id = "REQ-001"
        req2.requirement_id = "REQ-002"
        
        mock_standard = Mock()
        mock_standard.requirements = [req1, req2]
        
        mock_asset = Mock()
        mock_asset.id = "ASSET-1"

        res1 = RequirementResult("REQ-001", "", MappingProxyType({}), EvaluationState.PASS)
        res2 = RequirementResult("REQ-002", "", MappingProxyType({}), EvaluationState.FAIL)
        
        # Funzione "finta" che popola la cache per simulare il side-effect di _resolve
        def fake_resolve(req_id, standard, asset, cache):
            result = res1 if req_id == "REQ-001" else res2
            cache[req_id] = result
            return result
            
        engine._resolve = Mock(side_effect=fake_resolve)

        result = engine._evaluate_asset(mock_asset, mock_standard)

        assert result.asset_id == "ASSET-1"
        assert len(result.requirement_results) == 2
        assert result.verdict == EvaluationState.FAIL # Aggregazione di PASS + FAIL
        assert engine._resolve.call_count == 2


# ── 4. Test Valutazione Device (evaluate) ──

class TestEvaluationEngineEvaluateDevice:

    def test_evaluate_device_aggregates_all_assets(self, engine):
        """Verifica che evaluate iteri sugli asset e aggreghi il verdetto del device."""
        mock_device = Mock()
        mock_device.id = "DEVICE-1"
        
        asset1, asset2 = Mock(), Mock()
        mock_device.assets = {"ASSET-1": asset1, "ASSET-2": asset2}
        
        mock_standard = Mock()
        mock_standard.id = "STD-1"

        asset_res1 = AssetEvaluationResult("ASSET-1", (), EvaluationState.PASS)
        asset_res2 = AssetEvaluationResult("ASSET-2", (), EvaluationState.PASS)
        
        engine._evaluate_asset = Mock(side_effect=[asset_res1, asset_res2])

        result = engine.evaluate(mock_device, mock_standard)

        assert result.device_id == "DEVICE-1"
        assert len(result.asset_results) == 2
        assert result.verdict == EvaluationState.PASS # Aggregazione di PASS + PASS
        assert engine._evaluate_asset.call_count == 2