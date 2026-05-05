import pytest
from types import MappingProxyType
from core.domain.evaluation_standard.decision_tree import (
    DecisionTree, DecisionNode, LeafNode,
)
from core.domain.evaluation_standard.standard_verdict import StandardVerdict
from core.domain.evaluation_standard.evaluation_state import EvaluationState
from core.domain.evaluation_standard.exceptions import CycleDetectedError


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
def two_step_tree() -> DecisionTree:
    """n1 --True--> n2 --True--> PASS / --False--> FAIL
       n1 --False--> FAIL"""
    return DecisionTree(root="n1", nodes=[
        DecisionNode("n1", "Domanda 1?", "n2", "leaf_fail"),
        DecisionNode("n2", "Domanda 2?", "leaf_pass", "leaf_fail"),
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


# ── Costruzione ──

class TestDecisionTreeConstruction:

    def test_duplicate_node_raises(self):
        with pytest.raises(ValueError, match="ID duplicato"):
            DecisionTree(root="n1", nodes=[
                LeafNode("n1", StandardVerdict.PASS),
                LeafNode("n1", StandardVerdict.FAIL),
            ])

    def test_missing_root_raises(self):
        with pytest.raises(ValueError, match="nodo radice"):
            DecisionTree(root="missing", nodes=[
                LeafNode("n1", StandardVerdict.PASS),
            ])

    def test_single_leaf_as_root(self):
        """Un albero con solo un nodo foglia è valido."""
        tree = DecisionTree(root="leaf", nodes=[
            LeafNode("leaf", StandardVerdict.PASS),
        ])
        result = tree.evaluate(MappingProxyType({}))
        assert result == EvaluationState.PASS


# ── Valutazione ──

class TestDecisionTreeEvaluation:

    def test_pass_path(self, simple_tree):
        result = simple_tree.evaluate(MappingProxyType({"n1": True}))
        assert result == EvaluationState.PASS

    def test_fail_path(self, simple_tree):
        result = simple_tree.evaluate(MappingProxyType({"n1": False}))
        assert result == EvaluationState.FAIL

    def test_na_path(self, na_tree):
        result = na_tree.evaluate(MappingProxyType({"n1": False}))
        assert result == EvaluationState.NA

    def test_pending_when_answer_missing(self, simple_tree):
        result = simple_tree.evaluate(MappingProxyType({}))
        assert result == EvaluationState.PENDING

    def test_two_step_all_true(self, two_step_tree):
        result = two_step_tree.evaluate(MappingProxyType({"n1": True, "n2": True}))
        assert result == EvaluationState.PASS

    def test_two_step_partial_answers(self, two_step_tree):
        """Risposta solo al primo nodo: il secondo resta pendente."""
        result = two_step_tree.evaluate(MappingProxyType({"n1": True}))
        assert result == EvaluationState.PENDING

    def test_two_step_first_false(self, two_step_tree):
        """Se il primo nodo è False, va direttamente a FAIL senza chiedere il secondo."""
        result = two_step_tree.evaluate(MappingProxyType({"n1": False}))
        assert result == EvaluationState.FAIL

    def test_extra_answers_ignored(self, simple_tree):
        """Risposte a nodi inesistenti non causano errori."""
        result = simple_tree.evaluate(MappingProxyType({"n1": True, "n99": False}))
        assert result == EvaluationState.PASS


# ── Cicli ──

class TestDecisionTreeCycleDetection:

    def test_self_referencing_node(self):
        """Un nodo che rimanda a se stesso."""
        tree = DecisionTree(root="n1", nodes=[
            DecisionNode("n1", "Loop?", "n1", "n1"),
        ])
        with pytest.raises(CycleDetectedError):
            tree.evaluate(MappingProxyType({"n1": True}))

    def test_two_node_cycle(self):
        """Due nodi che si rimandano a vicenda."""
        tree = DecisionTree(root="n1", nodes=[
            DecisionNode("n1", "Q1?", "n2", "n2"),
            DecisionNode("n2", "Q2?", "n1", "n1"),
        ])
        with pytest.raises(CycleDetectedError):
            tree.evaluate(MappingProxyType({"n1": True, "n2": True}))