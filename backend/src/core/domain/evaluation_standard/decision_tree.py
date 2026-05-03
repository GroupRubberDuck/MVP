from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import MappingProxyType
from collections.abc import Sequence
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


@dataclass(frozen=True)
class DecisionNode(Node):
    """Un nodo che pone una domanda e divide il percorso."""
    node_id: str
    question: str
    child_on_true_id: str
    child_on_false_id: str
 
    def next(self, condition: bool | None) -> str | None:
        if condition is None:
            return None
        return self.child_on_true_id if condition else self.child_on_false_id
 
    @property
    def verdict(self) -> None:
        return None
 
    @property
    def id(self) -> str: 
        return self.node_id
@dataclass(frozen=True)
class LeafNode(Node):
    """Un nodo che rappresenta un verdetto finale."""
    node_id: str
    verdict_value: StandardVerdict
    
    @property
    def verdict(self) -> StandardVerdict:
        return self.verdict_value
    
    def next(self, condition: bool | None) -> None:
        return None
    
    @property
    def id(self) -> str: 
        return self.node_id
    

    
class DecisionTree:
 
    def __init__(self, root: str, nodes: Sequence[Node] | tuple[Node, ...]):
        # Costruzione del dizionario con validazione duplicati e root
        nodes_dict: dict[str, Node] = {}
        for node in nodes:
            if node.id in nodes_dict:
                raise ValueError(
                    f"ID duplicato: il nodo '{node.id}' è già presente.")
            nodes_dict[node.id] = node
 
        if root not in nodes_dict:
            raise ValueError(
                f"Il nodo radice '{root}' non esiste tra i nodi forniti.")
 
        self._root = root
        self._nodes = nodes_dict
 
    def evaluate(self, answers: MappingProxyType[str, bool]) -> EvaluationState:
        current_node_id = self._root
        visited: set[str] = set()
 
        while True:
            if current_node_id in visited:
                raise CycleDetectedError(
                    f"Ciclo infinito rilevato al nodo '{current_node_id}'.")
            visited.add(current_node_id)
 
            current_node = self._nodes.get(current_node_id)
            if current_node is None:
                raise ValueError(
                    f"Nodo '{current_node_id}' referenziato ma non presente nell'albero.")
 
            if current_node.verdict is not None:
                return EvaluationState.from_verdict(current_node.verdict)
 
            answer = answers.get(current_node_id)
            if answer is None:
                return EvaluationState.PENDING
 
            next_node_id = current_node.next(answer)
            if next_node_id is None:
                return EvaluationState.PENDING
 
            current_node_id = next_node_id
 
