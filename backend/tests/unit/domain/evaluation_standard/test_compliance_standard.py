import pytest
from core.domain.evaluation_standard.compliance_standard import ComplianceStandard
from core.domain.evaluation_standard.requirement import Requirement
from core.domain.evaluation_standard.decision_tree import (
    DecisionTree, DecisionNode, LeafNode,
)
from core.domain.evaluation_standard.standard_verdict import StandardVerdict
from core.domain.evaluation_standard.exceptions import RequirementNotFoundError


# ── Fixtures ──

@pytest.fixture
def simple_tree() -> DecisionTree:
    return DecisionTree(root="n1", nodes=[
        DecisionNode("n1", "Domanda?", "leaf_pass", "leaf_fail"),
        LeafNode("leaf_pass", StandardVerdict.PASS),
        LeafNode("leaf_fail", StandardVerdict.FAIL),
    ])


@pytest.fixture
def make_requirement(simple_tree):
    """Factory per creare requirement con ID diversi."""
    def _make(req_id: str = "REQ-001", dep_ids: tuple[str, ...] = ()) -> Requirement:
        return Requirement(
            requirement_id=req_id, name=f"Req {req_id}",
            description="desc", target_description="target",
            dependency_ids=dep_ids, decision_tree=simple_tree,
        )
    return _make


@pytest.fixture
def sample_standard(make_requirement) -> ComplianceStandard:
    return ComplianceStandard(
        standard_id="STD-1", name="EN 18031",
        version_number="1.0",
        requirements=[make_requirement("REQ-001"), make_requirement("REQ-002")],
    )


# ── Validazione costruzione ──

class TestComplianceStandardValidation:

    def test_empty_id_raises(self):
        with pytest.raises(ValueError, match="standard_id non può essere vuoto"):
            ComplianceStandard("", "EN 18031", "1.0", [])

    def test_empty_name_raises(self):
        with pytest.raises(ValueError, match="name non può essere vuoto"):
            ComplianceStandard("STD-1", "", "1.0", [])

    def test_duplicate_requirement_raises(self, make_requirement):
        req = make_requirement("REQ-001")
        with pytest.raises(ValueError, match="Requisito duplicato"):
            ComplianceStandard("STD-1", "EN 18031", "1.0", [req, req])


# ── Proprietà ──

class TestComplianceStandardProperties:

    def test_id(self, sample_standard):
        assert sample_standard.id == "STD-1"

    def test_name(self, sample_standard):
        assert sample_standard.name == "EN 18031"

    def test_version(self, sample_standard):
        assert sample_standard.version_number == "1.0"

    def test_requirements_returns_tuple(self, sample_standard):
        reqs = sample_standard.requirements
        assert isinstance(reqs, tuple)
        assert len(reqs) == 2

    def test_requirements_tuple_is_defensive_copy(self, sample_standard):
        """Modificare la tupla restituita non altera lo standard."""
        reqs1 = sample_standard.requirements
        reqs2 = sample_standard.requirements
        assert reqs1 is not reqs2
        assert reqs1 == reqs2


# ── get_requirement ──

class TestComplianceStandardGetRequirement:

    def test_get_existing(self, sample_standard, make_requirement):
        req = sample_standard.get_requirement("REQ-001")
        assert req.requirement_id == "REQ-001"

    def test_get_nonexistent_raises(self, sample_standard):
        with pytest.raises(RequirementNotFoundError):
            sample_standard.get_requirement("REQ-999")


# ── Immutabilità per costruzione ──

class TestComplianceStandardImmutability:

    def test_no_setter_for_id(self, sample_standard):
        with pytest.raises(AttributeError):
            sample_standard.id = "STD-2"

    def test_no_setter_for_name(self, sample_standard):
        with pytest.raises(AttributeError):
            sample_standard.name = "Altro"

    def test_no_add_requirement_method(self):
        assert not hasattr(ComplianceStandard, "add_requirement")

    def test_no_remove_requirement_method(self):
        assert not hasattr(ComplianceStandard, "remove_requirement")