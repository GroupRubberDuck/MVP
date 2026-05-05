import pytest
from unittest.mock import MagicMock
from types import MappingProxyType

from core.domain.evaluation_object.asset.asset import Asset
from core.domain.evaluation_object.asset.asset_anagraphic import AssetAnagraphic
from core.domain.evaluation_object.asset.asset_evidence import AssetEvidence
from core.domain.evaluation_object.asset.asset_proprieties import AssetProprieties
from core.domain.evaluation_object.asset.asset_type import AssetType
from core.domain.evaluation_object.device import Device

from core.ports.outbound.device.find_all_device_port import DeviceSummary

from adapters.outbound.device.mongo_device_repository import MongoDeviceAdapter


def _make_asset(asset_id: str = "A1", evidences: dict | None = None) -> Asset:
    return Asset(
        id=asset_id,
        anagraphic=AssetAnagraphic(
            name="Test Asset",
            asset_type=AssetType.NETWORK,
            description="Descrizione test",
        ),
        proprieties=AssetProprieties(evidences=evidences or {}),
    )


def _make_device(assets: list[Asset] | None = None) -> Device:
    return Device.create(
        device_id="DEV-1",
        standard_id="EN-18031",
        name="Smart Router",
        os="Linux",
        description="Router di test",
        assets=assets,
    )


def _make_evidence(req_id: str = "REQ-1",
                   choices: dict | None = None,
                   justification: str = "Giustificazione") -> AssetEvidence:
    return AssetEvidence(
        requirement_id=req_id,
        node_choices=MappingProxyType(choices or {"N1": True}),
        justification=justification,
    )


def _base_doc(assets: list | None = None) -> dict:
    return {
        "_id": "DEV-1",
        "name": "Smart Router",
        "os": "Linux",
        "description": "Router di test",
        "compliance_standard_id": "EN-18031",
        "assets": assets or [],
    }


def _asset_doc(asset_id: str = "A1", evaluations: list | None = None) -> dict:
    return {
        "id": asset_id,
        "name": "Test Asset",
        "type": "network",
        "description": "Descrizione test",
        "evaluations": evaluations or [],
    }


def _eval_doc(req_id: str = "REQ-1",
              choices: dict | None = None,
              justification: str = "Giustificazione") -> dict:
    return {
        "id": req_id,
        "evaluation_map": choices or {"N1": True},
        "justification": justification,
    }


@pytest.fixture
def collection():
    return MagicMock()


@pytest.fixture
def adapter(collection):
    return MongoDeviceAdapter(collection)


@pytest.fixture
def device_senza_asset():
    return _make_device()


@pytest.fixture
def device_con_asset():
    evidence = _make_evidence()
    asset = _make_asset("A1", evidences={"REQ-1": evidence})
    return _make_device(assets=[asset])


class TestRegister:

    def test_calls_insert_one(self, adapter, collection, device_senza_asset):
        adapter.register(device_senza_asset)
        collection.insert_one.assert_called_once()

    def test_document_has_correct_id(self, adapter, collection, device_senza_asset):
        adapter.register(device_senza_asset)
        doc = collection.insert_one.call_args[0][0]
        assert doc["_id"] == "DEV-1"

    def test_document_has_anagraphic_fields(self, adapter, collection, device_senza_asset):
        adapter.register(device_senza_asset)
        doc = collection.insert_one.call_args[0][0]
        assert doc["name"] == "Smart Router"
        assert doc["os"] == "Linux"
        assert doc["description"] == "Router di test"
        assert doc["compliance_standard_id"] == "EN-18031"

    def test_document_assets_are_serialized(self, adapter, collection, device_con_asset):
        adapter.register(device_con_asset)
        doc = collection.insert_one.call_args[0][0]
        assert len(doc["assets"]) == 1
        asset_doc = doc["assets"][0]
        assert asset_doc["id"] == "A1"
        assert asset_doc["type"] == "network"

    def test_evaluation_map_is_serialized(self, adapter, collection, device_con_asset):
        adapter.register(device_con_asset)
        doc = collection.insert_one.call_args[0][0]
        eval_doc = doc["assets"][0]["evaluations"][0]
        assert eval_doc["id"] == "REQ-1"
        assert eval_doc["evaluation_map"] == {"N1": True}
        assert eval_doc["justification"] == "Giustificazione"


class TestSave:

    def test_calls_replace_one(self, adapter, collection, device_senza_asset):
        adapter.save(device_senza_asset)
        collection.replace_one.assert_called_once()

    def test_filters_by_id(self, adapter, collection, device_senza_asset):
        adapter.save(device_senza_asset)
        filtro = collection.replace_one.call_args[0][0]
        assert filtro == {"_id": "DEV-1"}

    def test_document_has_no_redundant_id(self, adapter, collection, device_senza_asset):
        adapter.save(device_senza_asset)
        doc = collection.replace_one.call_args[0][1]
        assert "_id" not in doc



class TestDelete:

    def test_calls_delete_one(self, adapter, collection):
        adapter.delete("DEV-1")
        collection.delete_one.assert_called_once_with({"_id": "DEV-1"})



class TestFindById:

    def test_returns_device(self, adapter, collection):
        collection.find_one.return_value = _base_doc()
        device = adapter.find_by_id("DEV-1")
        assert device.id == "DEV-1"
        assert device.standard_id == "EN-18031"
        assert device.name == "Smart Router"

    def test_raises_key_error_if_not_found(self, adapter, collection):
        collection.find_one.return_value = None
        with pytest.raises(KeyError):
            adapter.find_by_id("INESISTENTE")

    def test_asset_is_reconstructed(self, adapter, collection):
        doc = _base_doc(assets=[_asset_doc()])
        collection.find_one.return_value = doc
        device = adapter.find_by_id("DEV-1")
        assert "A1" in device.assets
        assert device.assets["A1"].anagraphic.asset_type == AssetType.NETWORK

    def test_evidence_is_reconstructed(self, adapter, collection):
        doc = _base_doc(assets=[_asset_doc(evaluations=[_eval_doc()])])
        collection.find_one.return_value = doc
        device = adapter.find_by_id("DEV-1")
        evidence = device.assets["A1"].get_evidence("REQ-1")
        assert evidence is not None
        assert evidence.node_choices["N1"] is True
        assert evidence.justification == "Giustificazione"

    def test_asset_without_evaluations(self, adapter, collection):
        doc = _base_doc(assets=[_asset_doc(evaluations=[])])
        collection.find_one.return_value = doc
        device = adapter.find_by_id("DEV-1")
        assert device.assets["A1"].get_evidence("REQ-1") is None

    def test_device_without_assets(self, adapter, collection):
        collection.find_one.return_value = _base_doc()
        device = adapter.find_by_id("DEV-1")
        assert len(device.assets) == 0


class TestFindAll:

    def test_returns_summary_list(self, adapter, collection):
        collection.find.return_value = [_base_doc()]
        result = adapter.find_all()
        assert len(result) == 1
        assert isinstance(result[0], DeviceSummary)

    def test_summary_has_correct_fields(self, adapter, collection):
        collection.find.return_value = [_base_doc()]
        summary = adapter.find_all()[0]
        assert summary.device_id == "DEV-1"
        assert summary.name == "Smart Router"
        assert summary.os == "Linux"
        assert summary.compliance_standard_id == "EN-18031"

    def test_projection_excludes_assets(self, adapter, collection):
        collection.find.return_value = []
        adapter.find_all()
        _, kwargs_or_proj = collection.find.call_args[0]
        assert kwargs_or_proj == {"assets": 0}

    def test_empty_list(self, adapter, collection):
        collection.find.return_value = []
        assert adapter.find_all() == []

    def test_multiple_devices(self, adapter, collection):
        doc2 = _base_doc()
        doc2["_id"] = "DEV-2"
        doc2["name"] = "Switch"
        collection.find.return_value = [_base_doc(), doc2]
        result = adapter.find_all()
        assert len(result) == 2
        assert result[1].device_id == "DEV-2"