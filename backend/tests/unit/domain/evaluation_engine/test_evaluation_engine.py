import pytest
from types import MappingProxyType

from core.domain.evaluation_object.device import Device
from core.domain.evaluation_object.asset import Asset
from core.domain.evaluation_object.answer import Answer
from core.domain.evaluation_object.asset_type import AssetType
from core.domain.evaluation_standard.compliance_standard import ComplianceStandard
from core.domain.evaluation_standard.requirement import Requirement
from core.domain.evaluation_standard.evaluation_state import EvaluationState
from core.domain.evaluation_engine.evaluation_result import RequirementResult
from core.domain.evaluation_standard.decision_tree import DecisionTree, DecisionNode, LeafNode
from core.domain.evaluation_standard.standard_verdict import StandardVerdict
from core.domain.evaluation_engine.evaluation_engine import EvaluationEngine


# ─────────────────────────────────────────────────────────────────────────────
# Helpers per costruire alberi decisionali minimali
# ─────────────────────────────────────────────────────────────────────────────

def make_tree_always_pass() -> DecisionTree:
    """Albero che restituisce sempre PASS indipendentemente dalle risposte."""
    return DecisionTree(
        root="leaf-pass",
        nodes=[LeafNode("leaf-pass", StandardVerdict.PASS)],
    )


def make_tree_always_fail() -> DecisionTree:
    """Albero che restituisce sempre FAIL indipendentemente dalle risposte."""
    return DecisionTree(
        root="leaf-fail",
        nodes=[LeafNode("leaf-fail", StandardVerdict.FAIL)],
    )


def make_tree_single_question(node_id: str) -> DecisionTree:
    """
    Albero con una singola domanda sul nodo node_id.
    True  → PASS
    False → FAIL
    Risposta assente → PENDING
    """
    return DecisionTree(
        root=node_id,
        nodes=[
            DecisionNode(node_id, "Domanda?", "leaf-pass", "leaf-fail"),
            LeafNode("leaf-pass", StandardVerdict.PASS),
            LeafNode("leaf-fail", StandardVerdict.FAIL),
        ],
    )


def make_requirement(requirement_id: str,
                     tree: DecisionTree | None = None,
                     dependency_ids: tuple[str, ...] = ()) -> Requirement:
    return Requirement(
        requirement_id=requirement_id,
        name=f"Requisito {requirement_id}",
        description=f"Descrizione {requirement_id}",
        target_description=f"Target {requirement_id}",
        dependency_ids=dependency_ids,
        decision_tree=tree or make_tree_always_pass(),
    )


def make_standard(requirements: list[Requirement]) -> ComplianceStandard:
    return ComplianceStandard(
        standard_id="std-1",
        name="Standard di test",
        version_number="1.0",
        requirements=requirements,
    )


def make_asset(asset_id: str, answers: list[Answer] | None = None) -> Asset:
    return Asset.create(
        asset_id=asset_id,
        name=f"Asset {asset_id}",
        asset_type=AssetType.SECURITY,
        description="Desc",
        answers=answers,
    )


def make_device(assets: list[Asset] | None = None) -> Device:
    return Device.create(
        device_id="device-1",
        standard_id="std-1",
        name="Device 1",
        os="Android",
        description="Desc",
        assets=assets,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def engine() -> EvaluationEngine:
    return EvaluationEngine()


# ─────────────────────────────────────────────────────────────────────────────
# _check_dependencies
# ─────────────────────────────────────────────────────────────────────────────

class TestCheckDependencies:

    @pytest.mark.requirement("REQ-ENG-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_no_dependencies_returns_none(self, engine):
        """Senza dipendenze la valutazione non è bloccata."""
        assert engine._check_dependencies(()) is None

    @pytest.mark.requirement("REQ-ENG-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_all_pass_returns_none(self, engine):
        """Se tutte le dipendenze sono PASS la valutazione non è bloccata."""
        deps = (("req-1", EvaluationState.PASS), ("req-2", EvaluationState.PASS))
        assert engine._check_dependencies(deps) is None

    @pytest.mark.requirement("REQ-ENG-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_fail_blocks(self, engine):
        """Una dipendenza FAIL blocca con FAIL."""
        deps = (("req-1", EvaluationState.FAIL),)
        assert engine._check_dependencies(deps) == EvaluationState.FAIL

    @pytest.mark.requirement("REQ-ENG-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_pending_blocks(self, engine):
        """Una dipendenza PENDING blocca con PENDING."""
        deps = (("req-1", EvaluationState.PENDING),)
        assert engine._check_dependencies(deps) == EvaluationState.PENDING

    @pytest.mark.requirement("REQ-ENG-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_na_blocks(self, engine):
        """Una dipendenza NA blocca con NA."""
        deps = (("req-1", EvaluationState.NA),)
        assert engine._check_dependencies(deps) == EvaluationState.NA

    @pytest.mark.requirement("REQ-ENG-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_fail_has_priority_over_pending(self, engine):
        """FAIL ha priorità su PENDING."""
        deps = (
            ("req-1", EvaluationState.PENDING),
            ("req-2", EvaluationState.FAIL),
        )
        assert engine._check_dependencies(deps) == EvaluationState.FAIL

    @pytest.mark.requirement("REQ-ENG-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_fail_has_priority_over_na(self, engine):
        """FAIL ha priorità su NA."""
        deps = (
            ("req-1", EvaluationState.NA),
            ("req-2", EvaluationState.FAIL),
        )
        assert engine._check_dependencies(deps) == EvaluationState.FAIL

    @pytest.mark.requirement("REQ-ENG-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_pending_has_priority_over_na(self, engine):
        """PENDING ha priorità su NA."""
        deps = (
            ("req-1", EvaluationState.NA),
            ("req-2", EvaluationState.PENDING),
        )
        assert engine._check_dependencies(deps) == EvaluationState.PENDING


# ─────────────────────────────────────────────────────────────────────────────
# _aggregate_evaluation_states
# ─────────────────────────────────────────────────────────────────────────────

class TestAggregateEvaluationStates:

    @pytest.mark.requirement("REQ-ENG-02")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_empty_states_returns_pass(self, engine):
        """Nessuno stato da aggregare restituisce PASS."""
        assert engine._aggregate_evaluation_states(()) == EvaluationState.PASS

    @pytest.mark.requirement("REQ-ENG-02")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_all_pass_returns_pass(self, engine):
        states = (EvaluationState.PASS, EvaluationState.PASS)
        assert engine._aggregate_evaluation_states(states) == EvaluationState.PASS

    @pytest.mark.requirement("REQ-ENG-02")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_na_is_neutral(self, engine):
        """NA non influenza l'aggregazione — trattato come PASS."""
        states = (EvaluationState.PASS, EvaluationState.NA)
        assert engine._aggregate_evaluation_states(states) == EvaluationState.PASS

    @pytest.mark.requirement("REQ-ENG-02")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_any_fail_returns_fail(self, engine):
        states = (EvaluationState.PASS, EvaluationState.FAIL)
        assert engine._aggregate_evaluation_states(states) == EvaluationState.FAIL

    @pytest.mark.requirement("REQ-ENG-02")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_any_pending_without_fail_returns_pending(self, engine):
        states = (EvaluationState.PASS, EvaluationState.PENDING)
        assert engine._aggregate_evaluation_states(states) == EvaluationState.PENDING

    @pytest.mark.requirement("REQ-ENG-02")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_fail_has_priority_over_pending(self, engine):
        states = (EvaluationState.PENDING, EvaluationState.FAIL)
        assert engine._aggregate_evaluation_states(states) == EvaluationState.FAIL


# ─────────────────────────────────────────────────────────────────────────────
# _evaluate_requirement
# ─────────────────────────────────────────────────────────────────────────────

class TestEvaluateRequirement:

    @pytest.mark.requirement("REQ-ENG-03")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_no_answer_returns_pending(self, engine):
        """Senza risposta e senza dipendenze bloccanti il requisito è PENDING."""
        req = make_requirement("req-1", make_tree_always_pass())
        result = engine._evaluate_requirement(req, answer=None, )
        assert result.state == EvaluationState.PENDING
        assert result.justification == ""
        assert len(result.node_choices) == 0

    @pytest.mark.requirement("REQ-ENG-03")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_answer_evaluated_correctly(self, engine):
        """Con risposta viene eseguita la valutazione dell'albero decisionale."""
        req = make_requirement("req-1", make_tree_always_pass())
        answer = Answer.create("req-1", justification="Conforme", node_choices={"node-1": True})
        result = engine._evaluate_requirement(req, answer=answer)
        assert result.state == EvaluationState.PASS
        assert result.justification == "Conforme"

    @pytest.mark.requirement("REQ-ENG-03")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_blocked_by_fail_dependency(self, engine):
        """Una dipendenza FAIL blocca la valutazione e restituisce FAIL."""
        req = make_requirement("req-1", make_tree_always_pass(), dependency_ids=("req-0",))
        answer = Answer.create("req-1", node_choices={"node-1": True})
        deps = (("req-0", EvaluationState.FAIL),)
        result = engine._evaluate_requirement(req, answer=answer, dependencies=deps)
        assert result.state == EvaluationState.FAIL

    @pytest.mark.requirement("REQ-ENG-03")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_blocked_by_pending_dependency(self, engine):
        """Una dipendenza PENDING blocca la valutazione e restituisce PENDING."""
        req = make_requirement("req-1", make_tree_always_pass())
        deps = (("req-0", EvaluationState.PENDING),)
        result = engine._evaluate_requirement(req, answer=None, dependencies=deps)
        assert result.state == EvaluationState.PENDING

    @pytest.mark.requirement("REQ-ENG-03")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_blocked_by_na_dependency(self, engine):
        """Una dipendenza NA blocca la valutazione e restituisce NA."""
        req = make_requirement("req-1", make_tree_always_pass(), dependency_ids=("req-0",))
        deps = (("req-0", EvaluationState.NA),)
        result = engine._evaluate_requirement(req, answer=None, dependencies=deps)
        assert result.state == EvaluationState.NA

    @pytest.mark.requirement("REQ-ENG-03")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_blocked_preserves_answer_data(self, engine):
        """
        Quando bloccato da dipendenze, il RequirementResult deve comunque
        contenere i dati della risposta dell'utente (justification, node_choices).
        """
        req = make_requirement("req-1", make_tree_always_pass())
        answer = Answer.create("req-1", justification="Già compilato",
                               node_choices={"node-1": True})
        deps = (("req-0", EvaluationState.FAIL),)
        result = engine._evaluate_requirement(req, answer=answer, dependencies=deps)
        assert result.justification == "Già compilato"
        assert result.node_choices["node-1"] is True

    @pytest.mark.requirement("REQ-ENG-03")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_dependencies_stored_in_result(self, engine):
        """Le dipendenze vengono registrate nel RequirementResult."""
        req = make_requirement("req-1", make_tree_always_pass())
        deps = (("req-0", EvaluationState.PASS),)
        result = engine._evaluate_requirement(req, answer=None, dependencies=deps)
        assert ("req-0", EvaluationState.PASS) in result.dependencies


# ─────────────────────────────────────────────────────────────────────────────
# evaluate — integrazione
# ─────────────────────────────────────────────────────────────────────────────

class TestEvaluate:

    @pytest.mark.requirement("REQ-ENG-04")
    @pytest.mark.priority("high")
    @pytest.mark.type("integrazione")
    def test_device_metadata_in_result(self, engine):
        """Il risultato contiene i dati anagrafici di device e standard."""
        standard = make_standard([make_requirement("req-1")])
        device = make_device([make_asset("asset-1")])
        result = engine.evaluate(device, standard)
        assert result.device_id == "device-1"
        assert result.device_name == "Device 1"
        assert result.standard_id == "std-1"
        assert result.standard_name == "Standard di test"

    @pytest.mark.requirement("REQ-ENG-04")
    @pytest.mark.priority("high")
    @pytest.mark.type("integrazione")
    def test_all_pass(self, engine):
        """Tutti i requisiti con risposta e albero PASS → verdetto PASS."""
        standard = make_standard([make_requirement("req-1", make_tree_always_pass())])
        asset = make_asset("asset-1", answers=[
            Answer.create("req-1", node_choices={"node-1": True}),
        ])
        result = engine.evaluate(make_device([asset]), standard)
        assert result.verdict == EvaluationState.PASS

    @pytest.mark.requirement("REQ-ENG-04")
    @pytest.mark.priority("high")
    @pytest.mark.type("integrazione")
    def test_any_fail_makes_device_fail(self, engine):
        """Un requisito FAIL rende il device FAIL."""
        standard = make_standard([
            make_requirement("req-1", make_tree_always_pass()),
            make_requirement("req-2", make_tree_always_fail()),
        ])
        asset = make_asset("asset-1", answers=[
            Answer.create("req-1", node_choices={}),
            Answer.create("req-2", node_choices={}),
        ])
        result = engine.evaluate(make_device([asset]), standard)
        assert result.verdict == EvaluationState.FAIL

    @pytest.mark.requirement("REQ-ENG-04")
    @pytest.mark.priority("high")
    @pytest.mark.type("integrazione")
    def test_missing_answer_makes_pending(self, engine):
        """Un requisito senza risposta rende il device PENDING."""
        standard = make_standard([make_requirement("req-1", make_tree_always_pass())])
        asset = make_asset("asset-1", answers=[])  # nessuna risposta
        result = engine.evaluate(make_device([asset]), standard)
        assert result.verdict == EvaluationState.PENDING

    @pytest.mark.requirement("REQ-ENG-04")
    @pytest.mark.priority("high")
    @pytest.mark.type("integrazione")
    def test_multiple_assets_aggregated(self, engine):
        """Il verdetto del device aggrega i verdetti di tutti gli asset."""
        standard = make_standard([make_requirement("req-1", make_tree_always_pass())])
        asset_ok = make_asset("asset-1", answers=[Answer.create("req-1", node_choices={})])
        asset_pending = make_asset("asset-2", answers=[])  # nessuna risposta
        result = engine.evaluate(make_device([asset_ok, asset_pending]), standard)
        assert result.verdict == EvaluationState.PENDING

    @pytest.mark.requirement("REQ-ENG-04")
    @pytest.mark.priority("high")
    @pytest.mark.type("integrazione")
    def test_asset_without_requirements_is_pass(self, engine):
        """Un device senza requisiti nello standard ha verdetto PASS."""
        standard = make_standard([])
        result = engine.evaluate(make_device([make_asset("asset-1")]), standard)
        assert result.verdict == EvaluationState.PASS

    # --- dipendenze ---

    @pytest.mark.requirement("REQ-ENG-05")
    @pytest.mark.priority("high")
    @pytest.mark.type("integrazione")
    def test_dependency_pass_allows_evaluation(self, engine):
        """
        req-2 dipende da req-1. Se req-1 è PASS, req-2 viene valutato normalmente.
        """
        standard = make_standard([
            make_requirement("req-1", make_tree_always_pass()),
            make_requirement("req-2", make_tree_always_pass(), dependency_ids=("req-1",)),
        ])
        asset = make_asset("asset-1", answers=[
            Answer.create("req-1", node_choices={}),
            Answer.create("req-2", node_choices={}),
        ])
        result = engine.evaluate(make_device([asset]), standard)
        req2 = result.get_asset_result("asset-1").get_requirement_result("req-2")
        assert req2.state == EvaluationState.PASS
        assert not req2.was_blocked_by_dependencies()

    @pytest.mark.requirement("REQ-ENG-05")
    @pytest.mark.priority("high")
    @pytest.mark.type("integrazione")
    def test_dependency_fail_blocks_dependent(self, engine):
        """
        req-2 dipende da req-1. Se req-1 è FAIL, req-2 è FAIL senza essere valutato.
        """
        standard = make_standard([
            make_requirement("req-1", make_tree_always_fail()),
            make_requirement("req-2", make_tree_always_pass(), dependency_ids=("req-1",)),
        ])
        asset = make_asset("asset-1", answers=[
            Answer.create("req-1", node_choices={}),
            Answer.create("req-2", node_choices={}),
        ])
        result = engine.evaluate(make_device([asset]), standard)
        req2 = result.get_asset_result("asset-1").get_requirement_result("req-2")
        assert req2.state == EvaluationState.FAIL
        assert req2.was_blocked_by_dependencies()

    @pytest.mark.requirement("REQ-ENG-05")
    @pytest.mark.priority("high")
    @pytest.mark.type("integrazione")
    def test_dependency_pending_blocks_dependent(self, engine):
        """
        req-2 dipende da req-1. Se req-1 è PENDING, req-2 è PENDING.
        """
        standard = make_standard([
            make_requirement("req-1", make_tree_single_question("req-1")),
            make_requirement("req-2", make_tree_always_pass(), dependency_ids=("req-1",)),
        ])
        # Nessuna risposta per req-1 → PENDING
        asset = make_asset("asset-1", answers=[
            Answer.create("req-2", node_choices={}),
        ])
        result = engine.evaluate(make_device([asset]), standard)
        req2 = result.get_asset_result("asset-1").get_requirement_result("req-2")
        assert req2.state == EvaluationState.PENDING
        assert req2.was_blocked_by_dependencies()

    @pytest.mark.requirement("REQ-ENG-05")
    @pytest.mark.priority("high")
    @pytest.mark.type("integrazione")
    def test_dependency_na_blocks_dependent_with_na(self, engine):
        """
        req-2 dipende da req-1. Se req-1 è NA, req-2 è NA.
        """
        standard = make_standard([
            make_requirement("req-1", DecisionTree(
                root="leaf-na",
                nodes=[LeafNode("leaf-na", StandardVerdict.NA)]
            )),
            make_requirement("req-2", make_tree_always_pass(), dependency_ids=("req-1",)),
        ])
        asset = make_asset("asset-1", answers=[
            Answer.create("req-1", node_choices={}),
            Answer.create("req-2", node_choices={}),
        ])
        result = engine.evaluate(make_device([asset]), standard)
        req2 = result.get_asset_result("asset-1").get_requirement_result("req-2")
        assert req2.state == EvaluationState.NA
        assert req2.was_blocked_by_dependencies()

    @pytest.mark.requirement("REQ-ENG-05")
    @pytest.mark.priority("high")
    @pytest.mark.type("integrazione")
    def test_dependency_resolved_regardless_of_order(self, engine):
        """
        req-1 dipende da req-2, ma nello standard req-1 viene prima di req-2.
        La valutazione ricorsiva con cache deve gestire correttamente l'ordine inverso.
        """
        standard = make_standard([
            # req-1 prima nello standard, ma dipende da req-2
            make_requirement("req-1", make_tree_always_pass(), dependency_ids=("req-2",)),
            make_requirement("req-2", make_tree_always_fail()),
        ])
        asset = make_asset("asset-1", answers=[
            Answer.create("req-1", node_choices={}),
            Answer.create("req-2", node_choices={}),
        ])
        result = engine.evaluate(make_device([asset]), standard)
        req1 = result.get_asset_result("asset-1").get_requirement_result("req-1")
        # req-2 è FAIL, quindi req-1 deve essere bloccato con FAIL
        assert req1.state == EvaluationState.FAIL
        assert req1.was_blocked_by_dependencies()

    @pytest.mark.requirement("REQ-ENG-05")
    @pytest.mark.priority("high")
    @pytest.mark.type("integrazione")
    def test_dependency_not_computed_twice(self, engine):
        """
        req-2 e req-3 dipendono entrambi da req-1.
        req-1 deve essere calcolato una sola volta (cache).
        Verifichiamo indirettamente che entrambi ricevano lo stesso stato di req-1.
        """
        standard = make_standard([
            make_requirement("req-1", make_tree_always_pass()),
            make_requirement("req-2", make_tree_always_pass(), dependency_ids=("req-1",)),
            make_requirement("req-3", make_tree_always_pass(), dependency_ids=("req-1",)),
        ])
        asset = make_asset("asset-1", answers=[
            Answer.create("req-1", node_choices={}),
            Answer.create("req-2", node_choices={}),
            Answer.create("req-3", node_choices={}),
        ])
        result = engine.evaluate(make_device([asset]), standard)
        asset_result = result.get_asset_result("asset-1")
        req2 = asset_result.get_requirement_result("req-2")
        req3 = asset_result.get_requirement_result("req-3")
        # Entrambi vedono req-1 come PASS nelle loro dipendenze
        assert ("req-1", EvaluationState.PASS) in req2.dependencies
        assert ("req-1", EvaluationState.PASS) in req3.dependencies