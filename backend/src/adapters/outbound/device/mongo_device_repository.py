from bson import ObjectId
from pymongo.collection import Collection

from core.domain.evaluation_standard.compliance_standard import ComplianceStandard
from core.domain.evaluation_standard.decision_tree import DecisionNode, DecisionTree, LeafNode, Node
from core.domain.evaluation_standard.requirement import Requirement
from core.domain.evaluation_standard.standard_verdict import StandardVerdict
from core.ports.outbound.compliance_standard.standard_repository import StandardRepository


class MongoStandardAdapter(StandardRepository):

    def __init__(self, collection: Collection) -> None:
        self._collection = collection

    def save(self, standard: ComplianceStandard) -> None:
        doc = self._to_document(standard)
        self._collection.replace_one(
            {"_id": ObjectId(standard.id)}, doc, upsert=True
        )

    def find_by_id(self, standard_id: str) -> ComplianceStandard:
        doc = self._collection.find_one({"_id": ObjectId(standard_id)})
        if doc is None:
            raise KeyError(f"Standard '{standard_id}' non trovato.")
        return self._from_document(doc)


    def _from_document(self, doc: dict) -> ComplianceStandard:
        requirements = [
            self._parse_requirement(req_doc)
            for req_doc in doc.get("requirements", [])
        ]
        return ComplianceStandard(
            standard_id=str(doc["_id"]),
            name=doc["name"],
            version_number=doc["version"],
            requirements=requirements,
        )

    def _parse_requirement(self, doc: dict) -> Requirement:
        nodes: list[Node] = []
        root_id = self._parse_node(doc["root_node"], nodes)
        tree = DecisionTree(root=root_id, nodes=nodes)
        return Requirement(
            requirement_id=doc["id"],
            name=doc["name"],
            description=doc["description"]["norm_description"],
            target_description=doc["description"]["target_description"],
            dependency_ids=tuple(dep["id"] for dep in doc.get("dependencies", [])),
            decision_tree=tree,
        )

    def _parse_node(self, doc: dict, nodes: list[Node]) -> str:
        node_id = doc["id"]
        if "result" in doc:
            nodes.append(LeafNode(
                node_id=node_id,
                verdict_value=StandardVerdict(doc["result"]),
            ))
        else:
            self._parse_node(doc["child_yes"], nodes)
            self._parse_node(doc["child_no"], nodes)
            nodes.append(DecisionNode(
                node_id=node_id,
                question=doc["description"],
                child_on_true_id=doc["child_yes"]["id"],
                child_on_false_id=doc["child_no"]["id"],
            ))
        return node_id

    def _to_document(self, standard: ComplianceStandard) -> dict:
        return {
            "name": standard.name,
            "version": standard.version_number,
            "requirements": [
                self._serialize_requirement(req)
                for req in standard.requirements
            ],
        }

    def _serialize_requirement(self, req: Requirement) -> dict:
        nodes_dict = req.decision_tree._nodes
        root_id = req.decision_tree._root
        return {
            "id": req.requirement_id,
            "name": req.name,
            "description": {
                "norm_description": req.description,
                "target_description": req.target_description,
            },
            "root_node": self._serialize_node(root_id, nodes_dict),
            "dependencies": [{"id": dep_id} for dep_id in req.dependency_ids],
        }

    def _serialize_node(self, node_id: str, nodes_dict: dict) -> dict:
        node = nodes_dict[node_id]
        if isinstance(node, LeafNode):
            return {"id": node.node_id, "result": node.verdict.value}
        return {
            "id": node.node_id,
            "description": node.question,
            "child_yes": self._serialize_node(node.child_on_true_id, nodes_dict),
            "child_no": self._serialize_node(node.child_on_false_id, nodes_dict),
        }