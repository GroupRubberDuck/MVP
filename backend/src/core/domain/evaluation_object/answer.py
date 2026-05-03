# answer.py
from dataclasses import dataclass, field
from types import MappingProxyType
@dataclass(frozen=True)
class Answer:
    requirement_id: str
    node_choices: MappingProxyType[str, bool] = field(
        default_factory=lambda: MappingProxyType({})
    )
    justification: str = ""

    def with_node_choice(self, node_id: str, value: bool) -> "Answer":
        new_choices = dict(self.node_choices)
        new_choices[node_id] = value
        return Answer(
            requirement_id=self.requirement_id,
            node_choices=MappingProxyType(new_choices),
            justification=self.justification,
        )

    def with_justification(self, justification: str) -> "Answer":
        return Answer(
            requirement_id=self.requirement_id,
            node_choices=self.node_choices,
            justification=justification,
        )