from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal

from .evaluation_state import EvaluationState
from .standard_verdict import StandardVerdict
from .exceptions import CycleDetectedError

# --- DOMINIO ---


class Node(ABC):
    @property
    @abstractmethod
    def id(self) -> str: pass

    @abstractmethod
    def next(self, condition: bool | None) -> str | None: 
        pass

    @property # Ti consiglio vivamente di usare @property per i getter semplici!
    @abstractmethod
    def verdict(self) -> StandardVerdict | None: 
        pass


#     @abstractmethod
#     def create_snapshot(self) -> NodeSnapshot:
#         pass


class DecisionNode(Node):
    """Un nodo che pone una domanda e divide il percorso."""

    def __init__(
        self, node_id: str, question: str, child_on_true_id: str, child_on_false_id: str
    ):
        self._id = node_id
        self._question = question
        self._child_on_true_id = child_on_true_id
        self._child_on_false_id = child_on_false_id

    @property
    def id(self) -> str:
        return self._id

    def next(self, condition: bool | None) -> str | None:
        if condition is None:
            return None # Gestione sicura del None
        return self._child_on_true_id if condition else self._child_on_false_id

    @property
    def verdict(self) -> StandardVerdict | None:
        return None # Nessun @abstractmethod qui!

    @property
    def question(self) -> str:
        return self._question

    @property
    def child_on_true_id(self) -> str:
        return self._child_on_true_id

    @property
    def child_on_false_id(self) -> str:
        return self._child_on_false_id


class LeafNode(Node):
        """Un nodo che rappresenta un verdetto finale."""
        
        def __init__(self, node_id: str, verdict: StandardVerdict):
                self._id = node_id
                self._verdict = verdict
        
        @property
        def id(self) -> str:
                return self._id
        
        def next(self, condition: bool | None) -> None:
            return None

        @property
        def verdict(self) -> StandardVerdict:
            return self._verdict

class DecisionTree:
    def __init__(self, root: str, nodes: list[Node] | tuple[Node, ...]):
        self._root = root
        self._nodes: dict[str, Node] = {}
        for node in nodes:
            if node.id in self._nodes:
                raise ValueError(f"ID duplicato: Il nodo con id '{node.id}' è già presente.")
            self._nodes[node.id] = node

    def evaluate(self, answers: MappingProxyType[str, bool]) -> EvaluationState:
        current_node_id = self._root
        visited: set[str] = set()

        while True:
            # 1. Protezione dai loop infiniti
            if current_node_id in visited:
                raise CycleDetectedError(f"Rilevato ciclo infinito al nodo '{current_node_id}'.")
            visited.add(current_node_id)

            # 2. Recupero del nodo corrente
            current_node = self._nodes[current_node_id]

            # 3. Controllo Verdetto (Condizione di uscita 1: Percorso completato)
            # Dato che LeafNode.verdict ritorna uno StandardVerdict, possiamo uscire subito.
            if current_node.verdict is not None:
                return EvaluationState.from_verdict(current_node.verdict)

            # 4. Recupero Risposta (Condizione di uscita 2: Mancano dati)
            answer = answers.get(current_node_id)
            if answer is None:
                return EvaluationState.PENDING

            # 5. Navigazione al prossimo nodo
            next_node_id = current_node.next(answer)
            
            # Questo controllo if rassicura il type checker che next_node_id non è None
            # prima di riassegnarlo a current_node_id e ricominciare il ciclo.
            if next_node_id is None:
                return EvaluationState.PENDING
                
            current_node_id = next_node_id