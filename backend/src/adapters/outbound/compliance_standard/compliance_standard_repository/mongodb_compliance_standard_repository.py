from pymongo.collection import Collection

from core.ports.outbound.compliance_standard.find_standard_port import FindStandardPort
from core.ports.outbound.compliance_standard.exceptions import StandardNotFoundError

from core.domain.evaluation_standard.compliance_standard import ComplianceStandard
from core.domain.evaluation_standard.requirement import Requirement
from core.domain.evaluation_standard.standard_verdict import StandardVerdict
from core.domain.evaluation_standard.decision_tree import (
    DecisionNode,
    DecisionTree,
    LeafNode,
    Node
)


class MongoComplianceStandardAdapter(FindStandardPort):
    def __init__(self, collection: Collection) -> None:
        self._collection = collection

    def find_standard(self, standard_id: str) -> ComplianceStandard:
        doc = self._collection.find_one({"_id": standard_id})
        if doc is None:
            raise StandardNotFoundError(
                f"Standard '{standard_id}' non trovato nello storage."
            )
        return self._from_document(doc)

    def _from_document(self, doc: dict) -> ComplianceStandard:
        requirements = []
        for req_doc in doc.get("requirements", []):
            root = req_doc["decision_tree"]["root_node_id"]
            nodes: list[Node] = []
            for node_doc in req_doc["decision_tree"]["nodes"]:
                if node_doc["node_type"] == "decision_node":
                    nodes.append(
                        DecisionNode(
                            node_id=node_doc["node_id"],
                            question=node_doc["question"],
                            child_on_true_id=node_doc["child_yes"],
                            child_on_false_id=node_doc["child_no"],
                        )
                    )
                elif node_doc["node_type"] == "leaf_node":
                    nodes.append(
                        LeafNode(
                            node_id=node_doc["node_id"],
                            verdict_value=StandardVerdict(
                                node_doc["verdict"]
                            ),
                        )
                    )
            requirements.append(
                Requirement(
                    requirement_id=req_doc["id"],
                    name=req_doc["name"],
                    description=req_doc["description"]["norm_description"],
                    target_description=req_doc["description"]["target_description"],
                    decision_tree=DecisionTree(root=root, nodes=nodes),
                    dependency_ids=tuple(req_doc.get("dependency_ids", ()))
                )
            )
        return ComplianceStandard(
            standard_id=doc["_id"],
            name=doc["name"],
            version_number=doc["version_number"],
            requirements=requirements,
        )
