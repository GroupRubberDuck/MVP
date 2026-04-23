from pydantic import BaseModel, Enum
from abc import ABC

class Verdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NA = "NA"

class Requirement(BaseModel):
    code: str
    name: str
    description: str
    target: str

class ComplianceStandard(BaseModel):
    id: str
    code: str
    name: str
    version: str
    requirements: list[Requirement]

class Node(ABC):
    code: str

    def is_leaf(self) -> bool:
        pass

class LeafNode(Node, BaseModel):
    verdict: Verdict

class DecisionNode(Node, BaseModel):
    question: str

    def get_next_node(self, answer: bool) -> Node:
        pass

class DecisionTree(BaseModel):
    pass