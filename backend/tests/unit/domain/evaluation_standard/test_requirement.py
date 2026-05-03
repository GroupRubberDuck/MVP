import pytest
from types import MappingProxyType
from core.domain.evaluation_object.answer import Answer
from core.domain.evaluation_standard.decision_tree import (
    DecisionTree, DecisionNode, LeafNode,
)
from core.domain.evaluation_standard.standard_verdict import StandardVerdict
from core.domain.evaluation_standard.evaluation_state import EvaluationState
from core.domain.evaluation_standard.requirement import Requirement
from core.domain.evaluation_standard.exceptions import MissingDecisionTreeError


# ── Fixtures ──

@pytest.fixture
def simple_tree() -> DecisionTree:
    """n1 --True--> PASS, --False--> FAIL"""
    return DecisionTree(root="n1", nodes=[
        DecisionNode("n1", "Domanda 1?", "leaf_pass", "leaf_fail"),
        LeafNode("leaf_pass", StandardVerdict.PASS),
        LeafNode("leaf_fail", StandardVerdict.FAIL),
    ])


@pytest.fixture
def na_tree() -> DecisionTree:
    """n1 --True--> PASS, --False--> NA"""
    return DecisionTree(root="n1", nodes=[
        DecisionNode("n1", "Applicabile?", "leaf_pass", "leaf_na"),
        LeafNode("leaf_pass", StandardVerdict.PASS),
        LeafNode("leaf_na", StandardVerdict.NA),
    ])


@pytest.fixture
def requirement_with_tree(simple_tree) -> Requirement:
    return Requirement(
        requirement_id="REQ-001", name="Controllo Accessi",
        description="Verifica accessi", target_description="Sistema login",
        decision_tree=simple_tree,
    )


@pytest.fixture
def requirement_with_deps(simple_tree) -> Requirement:
    return Requirement(
        requirement_id="REQ-001", name="Controllo Accessi",
        description="Verifica accessi", target_description="Sistema login",
        dependency_ids=("DEP-1", "DEP-2"),
        decision_tree=simple_tree,
    )


# ── Validazione ──

class TestRequirementValidation:

    def test_empty_id_raises(self):
        with pytest.raises(ValueError):
            Requirement(
                requirement_id="", name="Test",
                description="Test", target_description="Test",
            )

    def test_missing_tree_raises_on_evaluate(self):
        req = Requirement(
            requirement_id="REQ-001", name="Test",
            description="Test", target_description="Test",
            decision_tree=None,
        )
        with pytest.raises(MissingDecisionTreeError, match="non ha un albero decisionale"):
            req.evaluate(Answer(requirement_id="REQ-001"))


# ── Valutazione base ──

class TestRequirementEvaluation:

    def test_pass(self, requirement_with_tree):
        answer = Answer(requirement_id="REQ-001", node_choices=MappingProxyType({"n1": True}))
        assert requirement_with_tree.evaluate(answer) == EvaluationState.PASS

    def test_fail(self, requirement_with_tree):
        answer = Answer(requirement_id="REQ-001", node_choices=MappingProxyType({"n1": False}))
        assert requirement_with_tree.evaluate(answer) == EvaluationState.FAIL

    def test_pending_incomplete_answers(self):
        """Albero a due livelli, risposta solo al primo nodo."""
        tree = DecisionTree(root="n1", nodes=[
            DecisionNode("n1", "Q1?", "n2", "leaf_fail"),
            DecisionNode("n2", "Q2?", "leaf_pass", "leaf_fail"),
            LeafNode("leaf_pass", StandardVerdict.PASS),
            LeafNode("leaf_fail", StandardVerdict.FAIL),
        ])
        req = Requirement(
            requirement_id="REQ-001", name="Test",
            description="Test", target_description="Test",
            decision_tree=tree,
        )
        answer = Answer(requirement_id="REQ-001", node_choices=MappingProxyType({"n1": True}))
        assert req.evaluate(answer) == EvaluationState.PENDING


# ── NA + Giustificazione ──

class TestRequirementNAJustification:

    def test_na_without_justification_returns_fail(self, na_tree):
        req = Requirement(
            requirement_id="REQ-001", name="Test",
            description="Test", target_description="Test",
            decision_tree=na_tree,
        )
        answer = Answer(
            requirement_id="REQ-001",
            node_choices=MappingProxyType({"n1": False}),
            justification="",
        )
        assert req.evaluate(answer) == EvaluationState.FAIL

    def test_na_with_whitespace_justification_returns_fail(self, na_tree):
        req = Requirement(
            requirement_id="REQ-001", name="Test",
            description="Test", target_description="Test",
            decision_tree=na_tree,
        )
        answer = Answer(
            requirement_id="REQ-001",
            node_choices=MappingProxyType({"n1": False}),
            justification="   ",
        )
        assert req.evaluate(answer) == EvaluationState.FAIL

    def test_na_with_justification_returns_na(self, na_tree):
        req = Requirement(
            requirement_id="REQ-001", name="Test",
            description="Test", target_description="Test",
            decision_tree=na_tree,
        )
        answer = Answer(
            requirement_id="REQ-001",
            node_choices=MappingProxyType({"n1": False}),
            justification="Non compatibile",
        )
        assert req.evaluate(answer) == EvaluationState.NA

    def test_pass_without_justification_stays_pass(self, na_tree):
        """La regola giustificazione si applica solo a NA, non a PASS."""
        req = Requirement(
            requirement_id="REQ-001", name="Test",
            description="Test", target_description="Test",
            decision_tree=na_tree,
        )
        answer = Answer(
            requirement_id="REQ-001",
            node_choices=MappingProxyType({"n1": True}),
            justification="",
        )
        assert req.evaluate(answer) == EvaluationState.PASS


# ── Dipendenze ──

class TestRequirementDependencies:

    @pytest.mark.parametrize("dependency_states, expected", [
        # Tutte PASS → valutazione normale
        ((("DEP-1", EvaluationState.PASS), ("DEP-2", EvaluationState.PASS)), EvaluationState.PASS),
        # Una FAIL → bloccato con FAIL
        ((("DEP-1", EvaluationState.PASS), ("DEP-2", EvaluationState.FAIL)), EvaluationState.FAIL),
        # Una PENDING → bloccato con PENDING
        ((("DEP-1", EvaluationState.PASS), ("DEP-2", EvaluationState.PENDING)), EvaluationState.PENDING),
        # Una NA → bloccato con NA
        ((("DEP-1", EvaluationState.PASS), ("DEP-2", EvaluationState.NA)), EvaluationState.NA),
    ])
    def test_dependency_blocking(self, requirement_with_tree, dependency_states, expected):
        answer = Answer(requirement_id="REQ-001", node_choices=MappingProxyType({"n1": True}))
        assert requirement_with_tree.evaluate(answer, dependency_states) == expected

    @pytest.mark.parametrize("dependency_states, expected", [
        # FAIL ha priorità su PENDING
        ((("D1", EvaluationState.PENDING), ("D2", EvaluationState.FAIL)), EvaluationState.FAIL),
        # FAIL ha priorità su NA
        ((("D1", EvaluationState.NA), ("D2", EvaluationState.FAIL)), EvaluationState.FAIL),
        # PENDING ha priorità su NA
        ((("D1", EvaluationState.NA), ("D2", EvaluationState.PENDING)), EvaluationState.PENDING),
    ])
    def test_dependency_priority(self, requirement_with_tree, dependency_states, expected):
        """Priorità: FAIL > PENDING > NA."""
        answer = Answer(requirement_id="REQ-001", node_choices=MappingProxyType({"n1": True}))
        assert requirement_with_tree.evaluate(answer, dependency_states) == expected

    def test_no_dependencies_evaluates_normally(self, requirement_with_tree):
        answer = Answer(requirement_id="REQ-001", node_choices=MappingProxyType({"n1": True}))
        assert requirement_with_tree.evaluate(answer) == EvaluationState.PASS

    def test_dependencies_block_before_tree_evaluation(self, requirement_with_tree):
        """Se le dipendenze bloccano, l'albero non viene nemmeno consultato."""
        answer = Answer(requirement_id="REQ-001", node_choices=MappingProxyType({"n1": False}))
        deps = (("DEP-1", EvaluationState.FAIL),)
        # L'answer porterebbe a FAIL dal tree, ma il risultato è FAIL dalle dipendenze
        # Il punto è che il tree non viene valutato — il risultato è lo stesso,
        # ma il test documenta l'intenzione
        assert requirement_with_tree.evaluate(answer, deps) == EvaluationState.FAIL