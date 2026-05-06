import pytest
from unittest.mock import Mock
from adapters.outbound.compliance_standard.compliance_standard_repository.mongodb_compliance_standard_repository import MongoComplianceStandardAdapter
from core.ports.outbound.compliance_standard.exceptions import StandardNotFoundError
from core.domain.evaluation_standard.compliance_standard import ComplianceStandard
# from core.domain.evaluation_standard.decision_tree import DecisionNode, LeafNode
# from core.domain.evaluation_standard.standard_verdict import StandardVerdict


# ── Fixtures ──


@pytest.fixture
def mock_collection():
    return Mock()


@pytest.fixture
def adapter(mock_collection):
    return MongoComplianceStandardAdapter(mock_collection)


def _make_standard_doc(
    standard_id="STD-001",
    name="EN 303 645",
    version_number="1.0",
    requirements=None,
):
    """Helper per costruire un documento MongoDB di standard."""
    if requirements is None:
        requirements = []
    return {
        "_id": standard_id,
        "name": name,
        "version_number": version_number,
        "requirements": requirements,
    }


def _make_requirement_doc(
    req_id="REQ-001",
    name="Access control",
    norm_description="Devices shall use access control.",
    target_description="All network interfaces",
    dependency_ids=None,
    root_node_id="N1",
    nodes=None,
):
    """Helper per costruire un sotto-documento di requirement."""
    if nodes is None:
        nodes = [
            {
                "node_id": "N1",
                "node_type": "decision_node",
                "question": "Is the equipment publicly accessible?",
                "child_yes": "L1",
                "child_no": "L2",
            },
            {
                "node_id": "L1",
                "node_type": "leaf_node",
                "verdict": "fail",
            },
            {
                "node_id": "L2",
                "node_type": "leaf_node",
                "verdict": "pass",
            },
        ]
    doc = {
        "id": req_id,
        "name": name,
        "description": {
            "norm_description": norm_description,
            "target_description": target_description,
        },
        "decision_tree": {
            "root_node_id": root_node_id,
            "nodes": nodes,
        },
    }
    if dependency_ids is not None:
        doc["dependency_ids"] = dependency_ids
    return doc


# ── find_standard ──


class TestFindStandard:

    def test_standard_not_found_raises(self, adapter, mock_collection):
        mock_collection.find_one.return_value = None

        with pytest.raises(StandardNotFoundError):
            adapter.find_standard("STD-999")

    def test_find_standard_returns_compliance_standard(self, adapter, mock_collection):
        doc = _make_standard_doc(requirements=[_make_requirement_doc()])
        mock_collection.find_one.return_value = doc

        result = adapter.find_standard("STD-001")

        assert isinstance(result, ComplianceStandard)
        assert result.id == "STD-001"
        assert result.name == "EN 303 645"
        assert result.version_number == "1.0"

    def test_find_standard_calls_collection_with_correct_filter(
        self, adapter, mock_collection
    ):
        mock_collection.find_one.return_value = _make_standard_doc(
            requirements=[_make_requirement_doc()]
        )

        adapter.find_standard("STD-001")

        mock_collection.find_one.assert_called_once_with({"_id": "STD-001"})


# ── Deserializzazione Requirements ──


class TestRequirementDeserialization:

    def test_single_requirement(self, adapter, mock_collection):
        doc = _make_standard_doc(requirements=[_make_requirement_doc()])
        mock_collection.find_one.return_value = doc

        result = adapter.find_standard("STD-001")

        assert len(result.requirements) == 1
        req = result.requirements[0]
        assert req.requirement_id == "REQ-001"
        assert req.name == "Access control"
        assert req.description == "Devices shall use access control."
        assert req.target_description == "All network interfaces"

    def test_multiple_requirements(self, adapter, mock_collection):
        doc = _make_standard_doc(
            requirements=[
                _make_requirement_doc(req_id="REQ-001"),
                _make_requirement_doc(req_id="REQ-002", name="Encryption"),
            ]
        )
        mock_collection.find_one.return_value = doc

        result = adapter.find_standard("STD-001")

        assert len(result.requirements) == 2
        ids = {r.requirement_id for r in result.requirements}
        assert ids == {"REQ-001", "REQ-002"}

    def test_empty_requirements(self, adapter, mock_collection):
        doc = _make_standard_doc(requirements=[])
        mock_collection.find_one.return_value = doc

        result = adapter.find_standard("STD-001")

        assert len(result.requirements) == 0

    def test_dependency_ids_preserved(self, adapter, mock_collection):
        doc = _make_standard_doc(
            requirements=[
                _make_requirement_doc(
                    req_id="REQ-002",
                    dependency_ids=["REQ-001"],
                ),
            ]
        )
        mock_collection.find_one.return_value = doc

        result = adapter.find_standard("STD-001")

        req = result.requirements[0]
        assert "REQ-001" in req.dependency_ids

    def test_missing_dependency_ids_defaults_to_empty(self, adapter, mock_collection):
        doc = _make_standard_doc(
            requirements=[_make_requirement_doc()]
        )
        mock_collection.find_one.return_value = doc

        result = adapter.find_standard("STD-001")

        req = result.requirements[0]
        assert len(req.dependency_ids) == 0


# ── Deserializzazione Decision Tree ──


class TestDecisionTreeDeserialization:

    def test_decision_node_deserialized(self, adapter, mock_collection):
        doc = _make_standard_doc(requirements=[_make_requirement_doc()])
        mock_collection.find_one.return_value = doc

        result = adapter.find_standard("STD-001")
        tree = result.requirements[0].decision_tree

        # L'albero di default ha N1 come decision node
        # Verifichiamo che valuti correttamente
        from types import MappingProxyType

        state = tree.evaluate(MappingProxyType({"N1": True}))
        # N1 true -> L1 (fail)
        from core.domain.evaluation_standard.evaluation_state import EvaluationState

        assert state == EvaluationState.FAIL

    def test_leaf_node_deserialized(self, adapter, mock_collection):
        doc = _make_standard_doc(requirements=[_make_requirement_doc()])
        mock_collection.find_one.return_value = doc

        result = adapter.find_standard("STD-001")
        tree = result.requirements[0].decision_tree

        from types import MappingProxyType
        from core.domain.evaluation_standard.evaluation_state import EvaluationState

        state = tree.evaluate(MappingProxyType({"N1": False}))
        # N1 false -> L2 (pass)
        assert state == EvaluationState.PASS

    def test_unanswered_node_returns_pending(self, adapter, mock_collection):
        doc = _make_standard_doc(requirements=[_make_requirement_doc()])
        mock_collection.find_one.return_value = doc

        result = adapter.find_standard("STD-001")
        tree = result.requirements[0].decision_tree

        from types import MappingProxyType
        from core.domain.evaluation_standard.evaluation_state import EvaluationState

        state = tree.evaluate(MappingProxyType({}))
        assert state == EvaluationState.PENDING

 