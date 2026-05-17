import pytest
from types import MappingProxyType
from unittest.mock import MagicMock

from core.domain.evaluation_engine.evaluation_detail import (
    DeviceEvaluationDetail,
    AssetEvaluationDetail,
    RequirementEvaluationDetail,
    NodeDetail,
)
from core.domain.evaluation_engine.evaluation_result import (
    DeviceEvaluationResult,
    AssetEvaluationResult,
    RequirementEvaluationResult,
)
from core.domain.evaluation_standard.evaluation_state import EvaluationState
from core.domain.evaluation_standard.decision_tree import (
    DecisionNode,
    LeafNode,
    DecisionTree,
)
from core.domain.evaluation_standard.standard_verdict import StandardVerdict
from core.domain.utilities.evaluation_detail_builder import EvaluationDetailBuilder 


@pytest.fixture
def builder():
    return EvaluationDetailBuilder()


# ── Helpers ──


def _make_decision_tree():
    nodes = [
        DecisionNode(
            node_id="N1",
            question="Is it publicly accessible?",
            child_on_true_id="N2",
            child_on_false_id="L1",
        ),
        DecisionNode(
            node_id="N2",
            question="Are there access controls?",
            child_on_true_id="L1",
            child_on_false_id="L2",
        ),
        LeafNode(node_id="L1", verdict_value=StandardVerdict.PASS),
        LeafNode(node_id="L2", verdict_value=StandardVerdict.FAIL),
    ]
    return DecisionTree(root="N1", nodes=nodes)


def _make_requirement(req_id="REQ-001", tree=None):
    req = MagicMock()
    req.requirement_id = req_id
    req.name = f"Requirement {req_id}"
    req.description = f"Description for {req_id}"
    req.target_description = f"Target for {req_id}"
    req.decision_tree = tree
    return req


def _make_requirement_result(req_id="REQ-001", state=EvaluationState.PASS):
    return RequirementEvaluationResult(
        requirement_id=req_id,
        state=state,
        node_choices=MappingProxyType({"N1": True}),
        justification="Test justification",
        dependencies=(),
    )


def _make_asset(asset_id="ASSET-1"):
    mock_anagraphic = MagicMock()
    mock_anagraphic.name = "Web Interface"
    mock_anagraphic.asset_type = "network_asset"
    mock_anagraphic.description = "Management interface"

    mock_asset = MagicMock()
    mock_asset.id = asset_id
    mock_asset.anagraphic = mock_anagraphic
    return mock_asset


def _make_device(device_id="DEV-1", assets=None):
    mock_device = MagicMock()
    mock_device.id = device_id
    mock_device.name = "Smart Thermostat"
    mock_device.os = "RTOS"
    mock_device.description = "IoT device"
    mock_device.standard_id = "STD-1"

    if assets:
        mock_device.get_asset.side_effect = lambda aid: next(
            a for a in assets if a.id == aid
        )

    return mock_device


def _make_standard(requirements=None):
    mock_standard = MagicMock()
    mock_standard.id = "STD-1"
    if requirements:
        mock_standard.get_requirement.side_effect = lambda rid: next(
            r for r in requirements if r.requirement_id == rid
        )
    return mock_standard


# ── RequirementDetail ──


class TestBuildRequirementDetail:
    

    def test_builds_detail_with_correct_fields(self, builder):
        """
        Dato un requisito di dominio completo di albero decisionale e il suo risultato di valutazione (Given),
        quando il builder viene invocato per generare i dettagli del requisito (When),
        allora deve creare un oggetto RequirementEvaluationDetail con tutti i campi anagrafici e di stato correttamente mappati (Then).
        """
        tree = _make_decision_tree()
        req = _make_requirement(tree=tree)
        result = _make_requirement_result()

        detail = builder.build_requirement_detail(result, req)

        assert isinstance(detail, RequirementEvaluationDetail)
        assert detail.requirement_id == "REQ-001"
        assert detail.name == req.name
        assert detail.description == req.description
        assert detail.target == req.target_description
        assert detail.justification == "Test justification"
        assert detail.state == EvaluationState.PASS
        assert detail.root_id == "N1"

    def test_nodes_are_flat_node_details(self, builder):
        """
        Dato un albero decisionale strutturato a grafi all'interno del requisito (Given),
        quando il builder genera il dettaglio (When),
        allora deve appiattire l'albero convertendo tutti i nodi in una mappa strutturata di oggetti NodeDetail (Then).
        """
        tree = _make_decision_tree()
        req = _make_requirement(tree=tree)
        result = _make_requirement_result()

        detail = builder.build_requirement_detail(result, req)

        assert len(detail.nodes) == 4
        for node in detail.nodes.values():
            assert isinstance(node, NodeDetail)

    def test_decision_node_has_correct_type(self, builder):
        """
        Dato un albero decisionale contenente nodi di tipo 'decisione' con relative domande (Given),
        quando viene generato il dettaglio appiattito (When),
        allora i NodeDetail corrispondenti devono avere il node_type impostato a 'decision' e mantenere i riferimenti ai figli (Then).
        """
        tree = _make_decision_tree()
        req = _make_requirement(tree=tree)
        result = _make_requirement_result()

        detail = builder.build_requirement_detail(result, req)

        n1 = detail.nodes["N1"]
        assert n1.node_type == "decision"
        assert n1.question == "Is it publicly accessible?"
        assert n1.child_on_true_id == "N2"
        assert n1.child_on_false_id == "L1"
        assert n1.verdict is None

    def test_leaf_node_has_correct_type(self, builder):
        """
        Dato un albero decisionale contenente nodi foglia con i verdetti finali (Given),
        quando viene generato il dettaglio appiattito (When),
        allora i NodeDetail corrispondenti devono avere node_type 'leaf', il corretto verdetto e campi figli nulli (Then).
        """
        tree = _make_decision_tree()
        req = _make_requirement(tree=tree)
        result = _make_requirement_result()

        detail = builder.build_requirement_detail(result, req)

        l1 = detail.nodes["L1"]
        assert l1.node_type == "leaf"
        assert l1.verdict == StandardVerdict.PASS
        assert l1.question is None
        assert l1.child_on_true_id is None
        assert l1.child_on_false_id is None

    def test_parent_ids_are_correct(self, builder):
        """
        Dato un albero decisionale complesso (Given),
        quando il builder calcola le relazioni per i NodeDetail (When),
        allora deve risolvere correttamente i puntatori 'parent_id', lasciando a None quello della radice e associando correttamente gli altri ai padri che li invocano (Then).
        """
        tree = _make_decision_tree()
        req = _make_requirement(tree=tree)
        result = _make_requirement_result()

        detail = builder.build_requirement_detail(result, req)

        assert detail.nodes["N1"].parent_id is None  # root
        assert detail.nodes["N2"].parent_id == "N1"
        assert detail.nodes["L1"].parent_id == "N2"  # N2 true -> L1
        assert detail.nodes["L2"].parent_id == "N2"

    def test_no_decision_tree_returns_empty_nodes(self, builder):
        """
        Dato un requisito che, per sua natura, è sprovvisto di un albero decisionale (Given),
        quando si tenta di generare il dettaglio (When),
        allora il dizionario dei nodi deve risultare vuoto e il root_id pari a una stringa vuota, senza sollevare errori (Then).
        """
        req = _make_requirement(tree=None)
        result = _make_requirement_result()

        detail = builder.build_requirement_detail(result, req)

        assert detail.nodes == MappingProxyType({})
        assert detail.root_id == ""

    def test_preserves_dependencies(self, builder):
        """
        Dato un risultato di valutazione che presenta dipendenze verso altri requisiti (Given),
        quando il builder istanzia il dettaglio del requisito (When),
        allora l'informazione sulle dipendenze deve essere preservata inalterata (Then).
        """
        tree = _make_decision_tree()
        req = _make_requirement(tree=tree)
        result = RequirementEvaluationResult(
            requirement_id="REQ-002",
            state=EvaluationState.FAIL,
            node_choices=MappingProxyType({}),
            justification="",
            dependencies=(("REQ-001", EvaluationState.FAIL),),
        )

        detail = builder.build_requirement_detail(result, req)

        assert detail.dependencies == (("REQ-001", EvaluationState.FAIL),)


# ── AssetDetail ──


class TestBuildAssetDetail:

    def test_builds_detail_with_correct_fields(self, builder):
        """
        Dato il risultato della valutazione di un asset assieme al device e allo standard associati (Given),
        quando viene richiesto il dettaglio dell'asset (When),
        allora il builder deve estrarre l'anagrafica dall'entità di dominio e aggregarla con il verdetto e i dettagli dei requisiti (Then).
        """
        tree = _make_decision_tree()
        req = _make_requirement(tree=tree)
        asset = _make_asset()
        device = _make_device(assets=[asset])
        standard = _make_standard(requirements=[req])

        req_result = _make_requirement_result()
        asset_result = AssetEvaluationResult(
            asset_id="ASSET-1",
            requirement_results=(req_result,),
            verdict=EvaluationState.PASS,
        )

        detail = builder.build_asset_detail(asset_result, device, standard)

        assert isinstance(detail, AssetEvaluationDetail)
        assert detail.asset_id == "ASSET-1"
        assert detail.name == "Web Interface"
        assert detail.asset_type == "network_asset"
        assert detail.description == "Management interface"
        assert detail.verdict == EvaluationState.PASS
        assert len(detail.requirement_details) == 1

    def test_multiple_requirements(self, builder):
        """
        Dato un asset valutato su più requisiti differenti (Given),
        quando il builder assembla il dettaglio complessivo (When),
        allora tutti i requirement_details devono essere correttamente processati, mappati e inclusi nell'oggetto restituito (Then).
        """
        tree = _make_decision_tree()
        req1 = _make_requirement(req_id="REQ-001", tree=tree)
        req2 = _make_requirement(req_id="REQ-002", tree=tree)
        asset = _make_asset()
        device = _make_device(assets=[asset])
        standard = _make_standard(requirements=[req1, req2])

        result1 = _make_requirement_result(req_id="REQ-001")
        result2 = _make_requirement_result(req_id="REQ-002", state=EvaluationState.FAIL)
        asset_result = AssetEvaluationResult(
            asset_id="ASSET-1",
            requirement_results=(result1, result2),
            verdict=EvaluationState.FAIL,
        )

        detail = builder.build_asset_detail(asset_result, device, standard)

        assert len(detail.requirement_details) == 2
        ids = {r.requirement_id for r in detail.requirement_details}
        assert ids == {"REQ-001", "REQ-002"}


# ── DeviceDetail ──


class TestBuildDeviceDetail:

    def test_builds_detail_with_correct_fields(self, builder):
        """
        Dato un risultato di valutazione root (DeviceEvaluationResult) e le relative entità Device e Standard (Given),
        quando il builder viene invocato per l'aggregazione finale (When),
        allora deve creare un DeviceEvaluationDetail estraendo correttamente l'anagrafica hardware e aggregando i dettagli di livello inferiore (Then).
        """
        tree = _make_decision_tree()
        req = _make_requirement(tree=tree)
        asset = _make_asset()
        device = _make_device(assets=[asset])
        standard = _make_standard(requirements=[req])

        req_result = _make_requirement_result()
        asset_result = AssetEvaluationResult(
            asset_id="ASSET-1",
            requirement_results=(req_result,),
            verdict=EvaluationState.PASS,
        )
        device_result = DeviceEvaluationResult(
            device_id="DEV-1",
            standard_id="STD-1",
            asset_results=(asset_result,),
            verdict=EvaluationState.PASS,
        )

        detail = builder.build_device_detail(device_result, device, standard)

        assert isinstance(detail, DeviceEvaluationDetail)
        assert detail.device_id == "DEV-1"
        assert detail.name == "Smart Thermostat"
        assert detail.operating_system == "RTOS"
        assert detail.description == "IoT device"
        assert detail.standard_id == "STD-1"
        assert detail.verdict == EvaluationState.PASS
        assert len(detail.asset_details) == 1

    def test_multiple_assets(self, builder):
        """
        Dato un dispositivo contenente molteplici asset valutati (Given),
        quando viene processato dal builder centrale (When),
        allora tutti i dettagli degli asset devono essere mappati in cascata e inclusi nell'oggetto restituito, preservando il verdetto aggregato globale (Then).
        """
        tree = _make_decision_tree()
        req = _make_requirement(tree=tree)

        asset1 = _make_asset(asset_id="ASSET-1")
        asset2 = _make_asset(asset_id="ASSET-2")
        device = _make_device(assets=[asset1, asset2])
        standard = _make_standard(requirements=[req])

        req_result = _make_requirement_result()
        asset_result1 = AssetEvaluationResult(
            asset_id="ASSET-1",
            requirement_results=(req_result,),
            verdict=EvaluationState.PASS,
        )
        asset_result2 = AssetEvaluationResult(
            asset_id="ASSET-2",
            requirement_results=(req_result,),
            verdict=EvaluationState.FAIL,
        )
        device_result = DeviceEvaluationResult(
            device_id="DEV-1",
            standard_id="STD-1",
            asset_results=(asset_result1, asset_result2),
            verdict=EvaluationState.FAIL,
        )

        detail = builder.build_device_detail(device_result, device, standard)

        assert len(detail.asset_details) == 2
        ids = {a.asset_id for a in detail.asset_details}
        assert ids == {"ASSET-1", "ASSET-2"}
        assert detail.verdict == EvaluationState.FAIL

    def test_empty_device(self, builder):
        """
        Dato un dispositivo anagraficamente valido ma privo di asset e valutazioni (Given),
        quando si tenta di generare il suo dettaglio di valutazione (When),
        allora il builder deve restituire un oggetto con la lista degli asset vuota gestendo correttamente l'assenza di dati (Then).
        """
        device = _make_device()
        standard = _make_standard()
        device_result = DeviceEvaluationResult(
            device_id="DEV-1",
            standard_id="STD-1",
            asset_results=(),
            verdict=EvaluationState.PASS,
        )

        detail = builder.build_device_detail(device_result, device, standard)

        assert detail.asset_details == ()
        assert detail.verdict == EvaluationState.PASS