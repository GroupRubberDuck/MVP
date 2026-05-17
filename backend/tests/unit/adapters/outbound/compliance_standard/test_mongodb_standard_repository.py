import pytest
from unittest.mock import Mock
from adapters.outbound.compliance_standard.mongodb_compliance_standard_repository import MongoComplianceStandardAdapter
from core.ports.outbound.compliance_standard.exceptions import StandardNotFoundError
from core.domain.evaluation_standard.compliance_standard import ComplianceStandard


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
        """
        Dato un ID di standard che non esiste nella collection MongoDB e per cui find_one restituisce None (Given),
        quando l'adapter tenta di recuperare lo standard tramite find_standard (When),
        allora deve sollevare un'eccezione StandardNotFoundError per segnalare l'assenza del documento (Then).
        """
        mock_collection.find_one.return_value = None

        with pytest.raises(StandardNotFoundError):
            adapter.find_standard("STD-999")

    def test_find_standard_returns_compliance_standard(self, adapter, mock_collection):
        """
        Dato un documento MongoDB valido e completo di uno standard con relativi requirements (Given),
        quando l'adapter lo recupera e lo deserializza tramite find_standard (When),
        allora deve restituire un'istanza di ComplianceStandard con ID, nome e numero di versione correttamente popolati (Then).
        """
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
        """
        Dato un ID standard da ricercare nel database (Given),
        quando viene invocato il metodo find_standard sull'adapter (When),
        allora la query MongoDB deve utilizzare esattamente il filtro {'_id': '<standard_id>'} per interrogare la collection (Then).
        """
        mock_collection.find_one.return_value = _make_standard_doc(
            requirements=[_make_requirement_doc()]
        )

        adapter.find_standard("STD-001")

        mock_collection.find_one.assert_called_once_with({"_id": "STD-001"})


# ── Deserializzazione Requirements ──


class TestRequirementDeserialization:

    def test_single_requirement(self, adapter, mock_collection):
        """
        Dato un documento standard contenente esattamente un requirement con tutti i campi valorizzati (Given),
        quando l'adapter deserializza il documento in un oggetto ComplianceStandard (When),
        allora la lista dei requirements deve contenere un solo elemento con ID, nome, descrizione normativa e descrizione target mappati correttamente (Then).
        """
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
        """
        Dato un documento standard con due requirements distinti identificati da REQ-001 e REQ-002 (Given),
        quando l'adapter completa la deserializzazione (When),
        allora la lista risultante deve contenere entrambi i requirements, ciascuno con il proprio ID univoco preservato (Then).
        """
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
        """
        Dato un documento standard la cui lista dei requirements è vuota (Given),
        quando viene eseguita la deserializzazione tramite l'adapter (When),
        allora l'oggetto ComplianceStandard risultante deve avere una lista di requirements vuota, senza errori di mapping (Then).
        """
        doc = _make_standard_doc(requirements=[])
        mock_collection.find_one.return_value = doc

        result = adapter.find_standard("STD-001")

        assert len(result.requirements) == 0

    def test_dependency_ids_preserved(self, adapter, mock_collection):
        """
        Dato un requirement con una lista di dependency_ids contenente riferimenti ad altri requirement (es. ['REQ-001']) (Given),
        quando l'adapter deserializza il documento MongoDB (When),
        allora la lista dependency_ids del requirement risultante deve contenere esattamente i valori specificati nel documento originale (Then).
        """
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
        """
        Dato un requirement il cui documento MongoDB non include il campo opzionale dependency_ids (Given),
        quando l'adapter lo deserializza in un oggetto di dominio (When),
        allora la proprietà dependency_ids deve essere inizializzata come una lista vuota, senza sollevare eccezioni (Then).
        """
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
        """
        Dato un requirement il cui decision tree include un nodo decisionale (decision_node) con risposta affermativa che porta a un leaf_node di fail (Given),
        quando l'albero viene deserializzato e valutato fornendo lo stato 'True' per il nodo N1 (When),
        allora il risultato della valutazione deve essere EvaluationState.FAIL, confermando la corretta ricostruzione della logica decisionale (Then).
        """
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
        """
        Dato un decision tree in cui la risposta negativa al nodo decisionale N1 conduce al leaf_node con verdetto 'pass' (Given),
        quando l'albero deserializzato viene valutato con lo stato 'False' per N1 (When),
        allora il verdetto restituito deve essere EvaluationState.PASS, dimostrando che i leaf_node sono stati correttamente mappati (Then).
        """
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
        """
        Dato un decision tree deserializzato correttamente ma valutato senza fornire alcuna risposta alle domande dei nodi decisionali (Given),
        quando il metodo evaluate viene chiamato con un dizionario di stati vuoto (When),
        allora il sistema deve restituire EvaluationState.PENDING, indicando che la valutazione non ha ancora prodotto un verdetto definitivo (Then).
        """
        doc = _make_standard_doc(requirements=[_make_requirement_doc()])
        mock_collection.find_one.return_value = doc

        result = adapter.find_standard("STD-001")
        tree = result.requirements[0].decision_tree

        from types import MappingProxyType
        from core.domain.evaluation_standard.evaluation_state import EvaluationState

        state = tree.evaluate(MappingProxyType({}))
        assert state == EvaluationState.PENDING

 