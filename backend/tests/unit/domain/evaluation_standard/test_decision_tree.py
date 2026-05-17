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
        """
        Dato un elenco di nodi per la costruzione dell'albero (Given),
        quando due o più nodi presentano lo stesso identificatore univoco (When),
        allora il sistema deve sollevare un ValueError impedendo la creazione di una struttura ambigua (Then).
        """
        with pytest.raises(ValueError, match="ID duplicato"):
            DecisionTree(root="n1", nodes=[
                LeafNode("n1", StandardVerdict.PASS),
                LeafNode("n1", StandardVerdict.FAIL),
            ])

    def test_missing_root_raises(self):
        """
        Dato un set di nodi validi (Given),
        quando l'identificatore del nodo radice (root) non corrisponde ad alcun nodo presente nell'elenco (When),
        allora deve essere sollevato un ValueError segnalando l'assenza del punto di ingresso (Then).
        """
        with pytest.raises(ValueError, match="nodo radice"):
            DecisionTree(root="missing", nodes=[
                LeafNode("n1", StandardVerdict.PASS),
            ])

    def test_single_leaf_as_root(self):
        """
        Dato un albero decisionale composto da un unico nodo foglia (Given),
        quando viene eseguita la valutazione (When),
        allora il sistema deve restituire immediatamente il verdetto della foglia senza richiedere input (Then).
        """
        tree = DecisionTree(root="leaf", nodes=[
            LeafNode("leaf", StandardVerdict.PASS),
        ])
        result = tree.evaluate(MappingProxyType({}))
        assert result == EvaluationState.PASS


# ── Valutazione ──

class TestDecisionTreeEvaluation:

    def test_pass_path(self, simple_tree):
        """
        Dato un albero decisionale semplice (Given),
        quando l'input dell'utente porta verso un nodo foglia di successo (PASS) (When),
        allora lo stato della valutazione deve risultare EvaluationState.PASS (Then).
        """
        result = simple_tree.evaluate(MappingProxyType({"n1": True}))
        assert result == EvaluationState.PASS

    def test_fail_path(self, simple_tree):
        """
        Dato un albero decisionale semplice (Given),
        quando l'input dell'utente porta verso un nodo foglia di fallimento (FAIL) (When),
        allora lo stato della valutazione deve risultare EvaluationState.FAIL (Then).
        """
        result = simple_tree.evaluate(MappingProxyType({"n1": False}))
        assert result == EvaluationState.FAIL

    def test_na_path(self, na_tree):
        """
        Dato un albero che prevede l'opzione di non applicabilità (NA) (Given),
        quando il percorso decisionale termina su una foglia NA (When),
        allora il risultato della valutazione deve essere mappato correttamente su EvaluationState.NA (Then).
        """
        result = na_tree.evaluate(MappingProxyType({"n1": False}))
        assert result == EvaluationState.NA

    def test_pending_when_answer_missing(self, simple_tree):
        """
        Dato un albero decisionale che richiede una risposta in un nodo specifico (Given),
        quando la mappa delle risposte non contiene il valore richiesto per quel nodo (When),
        allora il processo di valutazione deve interrompersi restituendo lo stato EvaluationState.PENDING (Then).
        """
        result = simple_tree.evaluate(MappingProxyType({}))
        assert result == EvaluationState.PENDING

    def test_two_step_all_true(self, two_step_tree):
        """
        Dato un albero decisionale a più livelli (Given),
        quando vengono fornite risposte coerenti che completano l'intero percorso fino a una foglia (When),
        allora deve essere restituito lo stato finale corrispondente alla foglia raggiunta (Then).
        """
        result = two_step_tree.evaluate(MappingProxyType({"n1": True, "n2": True}))
        assert result == EvaluationState.PASS

    def test_two_step_partial_answers(self, two_step_tree):
        """
        Dato un albero a più livelli (Given),
        quando viene fornita una risposta che sblocca il primo livello ma manca la risposta per il livello successivo (When),
        allora il sistema deve restituire PENDING indicando che la valutazione è incompleta (Then).
        """
        result = two_step_tree.evaluate(MappingProxyType({"n1": True}))
        assert result == EvaluationState.PENDING

    def test_two_step_first_false(self, two_step_tree):
        """
        Dato un albero a più livelli (Given),
        quando la prima risposta porta a un percorso che termina in una foglia saltando i nodi intermedi (When),
        allora il sistema deve ignorare la mancanza di risposte per i nodi non visitati e restituire il verdetto finale (Then).
        """
        result = two_step_tree.evaluate(MappingProxyType({"n1": False}))
        assert result == EvaluationState.FAIL

    def test_extra_answers_ignored(self, simple_tree):
        """
        Data una mappa di risposte (Given),
        quando contiene identificativi di nodi non appartenenti all'albero o non visitati durante il percorso (When),
        allora il sistema deve ignorare tali input supplementari e calcolare correttamente il verdetto basandosi solo sui nodi attraversati (Then).
        """
        result = simple_tree.evaluate(MappingProxyType({"n1": True, "n99": False}))
        assert result == EvaluationState.PASS


# ── Cicli ──

class TestDecisionTreeCycleDetection:

    def test_self_referencing_node(self):
        """
        Dato un nodo decisionale mal configurato che punta a se stesso come figlio (Given),
        quando viene avviata la valutazione (When),
        allora il sistema deve rilevare la ricorsione infinita e sollevare un CycleDetectedError (Then).
        """
        tree = DecisionTree(root="n1", nodes=[
            DecisionNode("n1", "Loop?", "n1", "n1"),
        ])
        with pytest.raises(CycleDetectedError):
            tree.evaluate(MappingProxyType({"n1": True}))

    def test_two_node_cycle(self):
        """
        Dato un albero contenente una dipendenza ciclica tra due o più nodi (Given),
        quando l'algoritmo di visita attraversa nuovamente un nodo già presente nel percorso corrente (When),
        allora deve essere sollevato un CycleDetectedError per prevenire il blocco del sistema (Then).
        """
        tree = DecisionTree(root="n1", nodes=[
            DecisionNode("n1", "Q1?", "n2", "n2"),
            DecisionNode("n2", "Q2?", "n1", "n1"),
        ])
        with pytest.raises(CycleDetectedError):
            tree.evaluate(MappingProxyType({"n1": True, "n2": True}))