from types import MappingProxyType
from dataclasses import dataclass

# --- 1. IL DTO / SNAPSHOT (Completamente immutabile) ---
@dataclass(frozen=True)
class SnapshotAnswer:
    requirement_id: str
    justification: str
    # Usiamo il ProxyType qui per garantire che il dizionario non sia modificabile
    node_choices: MappingProxyType[str, bool] 


# --- 2. L'ENTITÀ DI DOMINIO (Regole di business e stato mutabile nascosto) ---
class Answer:
    # Il costruttore costringe a creare l'oggetto in uno stato valido fin da subito
    def __init__(self, requirement_id: str,
                  justification: str = "",
                  node_choices: dict[str, bool] | None = None):
        self._requirement_id = requirement_id
        self._justification = justification
        # Inizializziamo il dizionario vuoto (o potresti passarlo al costruttore se serve)
        self._node_choices: dict[str, bool] = node_choices.copy() if node_choices is not None else {}

    @property
    def requirement_id(self) -> str:
        return self._requirement_id

    @property
    def justification(self) -> str:
        return self._justification  

    # Questo serve se vuoi leggere i dati "live" dell'entità senza fare uno snapshot
    @property
    def node_choices(self) -> MappingProxyType[str, bool]:
        return MappingProxyType(self._node_choices)
        
    def set_node_choice(self, node_id: str, value: bool):
        # Qui un domani potrai aggiungere la tua logica di dominio. Esempio:
        # if node_id == "": raise ValueError("Il nodo non può essere vuoto")
        self._node_choices[node_id] = value
    
    def set_justification(self, justification: str):
        
        # if len(justification) < 10: raise ValueError("La giustificazione deve essere più lunga")
        self._justification = justification

    # Il metodo per estrarre i dati in sicurezza verso l'esterno
    def create_snapshot(self) -> SnapshotAnswer:
        """"Crea uno snapshot immutabile dell'Answer, da usare per la lettura"""
        return SnapshotAnswer(
            requirement_id=self._requirement_id,
            justification=self._justification,
            node_choices=MappingProxyType(self._node_choices.copy())  # Copia per sicurezza 
        )