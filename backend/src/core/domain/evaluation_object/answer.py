# answer.py
from dataclasses import dataclass, field
from types import MappingProxyType

@dataclass
class Answer:
    requirement_id: str
    justification: str = ""
    _node_choices: dict[str, bool] = field(default_factory=dict, repr=False)

    # costruttore alternativo più comodo
    @classmethod
    def create(cls, requirement_id: str, 
               node_choices: dict[str, bool] | None = None,
               justification: str = "") -> "Answer":
        obj = cls(requirement_id, justification)
        obj._node_choices = dict(node_choices or {})
        return obj

    @property
    def node_choices(self) -> MappingProxyType[str, bool]:
        return MappingProxyType(self._node_choices)

    def set_node_choice(self, node_id: str, value: bool) -> None:
        self._node_choices[node_id] = value

    def set_justification(self, justification: str) -> None:
        self.justification = justification