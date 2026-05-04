import pytest
from types import MappingProxyType
from core.domain.evaluation_object.asset import (
    Asset,
    AssetAnagraphic,
    AssetEvidence,
    AssetProprieties,
    AssetType,
)


# ── Fixtures ──

@pytest.fixture
def anagraphic():
    return AssetAnagraphic(
        name="Network Interface",
        asset_type=AssetType.NETWORK,
        description="Ethernet controller",
    )


@pytest.fixture
def asset_vuoto(anagraphic):
    return Asset(id="ASSET-1", anagraphic=anagraphic)


@pytest.fixture
def asset_con_evidence(anagraphic):
    proprieties = AssetProprieties()
    proprieties.set_node_choice("REQ-001", "n1", True)
    return Asset(id="ASSET-1", anagraphic=anagraphic, proprieties=proprieties)


# ── AssetEvidence ──

class TestAssetEvidence:

    def test_default_empty(self):
        evidence = AssetEvidence(requirement_id="REQ-001")
        assert evidence.node_choices == MappingProxyType({})
        assert evidence.justification == ""

    def test_with_node_choice_returns_new_instance(self):
        original = AssetEvidence(requirement_id="REQ-001")
        updated = original.with_node_choice("n1", True)
        assert updated is not original
        assert updated.node_choices["n1"] is True
        assert "n1" not in original.node_choices

    def test_with_node_choice_preserves_justification(self):
        original = AssetEvidence(requirement_id="REQ-001", justification="test")
        updated = original.with_node_choice("n1", True)
        assert updated.justification == "test"

    def test_with_justification_returns_new_instance(self):
        original = AssetEvidence(
            requirement_id="REQ-001",
            node_choices=MappingProxyType({"n1": True}),
        )
        updated = original.with_justification("nuova")
        assert updated is not original
        assert updated.justification == "nuova"
        assert updated.node_choices["n1"] is True

    def test_frozen(self):
        evidence = AssetEvidence(requirement_id="REQ-001")
        with pytest.raises(AttributeError):
            evidence.justification = "modifica"


# ── AssetProprieties ──

class TestAssetProprieties:

    def test_empty_by_default(self):
        proprieties = AssetProprieties()
        assert len(proprieties.evidences) == 0

    def test_set_node_choice_creates_evidence_automatically(self):
        proprieties = AssetProprieties()
        proprieties.set_node_choice("REQ-001", "n1", True)
        evidence = proprieties.get_evidence("REQ-001")
        assert evidence is not None
        assert evidence.node_choices["n1"] is True

    def test_set_node_choice_preserves_existing(self):
        proprieties = AssetProprieties()
        proprieties.set_node_choice("REQ-001", "n1", True)
        proprieties.set_node_choice("REQ-001", "n2", False)
        evidence = proprieties.get_evidence("REQ-001")
        assert evidence.node_choices["n1"] is True
        assert evidence.node_choices["n2"] is False

    def test_set_justification_creates_evidence_automatically(self):
        proprieties = AssetProprieties()
        proprieties.set_justification("REQ-001", "giustificazione")
        evidence = proprieties.get_evidence("REQ-001")
        assert evidence is not None
        assert evidence.justification == "giustificazione"

    def test_set_justification_preserves_node_choices(self):
        proprieties = AssetProprieties()
        proprieties.set_node_choice("REQ-001", "n1", True)
        proprieties.set_justification("REQ-001", "giustificazione")
        evidence = proprieties.get_evidence("REQ-001")
        assert evidence.node_choices["n1"] is True
        assert evidence.justification == "giustificazione"

    def test_get_evidence_missing_returns_none(self):
        proprieties = AssetProprieties()
        assert proprieties.get_evidence("REQ-999") is None

    def test_evidences_immutable_view(self):
        proprieties = AssetProprieties()
        proprieties.set_node_choice("REQ-001", "n1", True)
        with pytest.raises(TypeError):
            proprieties.evidences["REQ-002"] = AssetEvidence(requirement_id="REQ-002")

    def test_init_with_existing_evidences(self):
        existing = {
            "REQ-001": AssetEvidence(
                requirement_id="REQ-001",
                node_choices=MappingProxyType({"n1": True}),
            )
        }
        proprieties = AssetProprieties(evidences=existing)
        assert proprieties.get_evidence("REQ-001").node_choices["n1"] is True


# ── Asset ──

class TestAssetCreation:

    def test_create_empty(self, asset_vuoto):
        assert asset_vuoto.id == "ASSET-1"
        assert len(asset_vuoto.proprieties.evidences) == 0

    def test_create_with_proprieties(self, asset_con_evidence):
        evidence = asset_con_evidence.proprieties.get_evidence("REQ-001")
        assert evidence is not None
        assert evidence.node_choices["n1"] is True

    def test_frozen_id(self, asset_vuoto):
        with pytest.raises(AttributeError):
            asset_vuoto.id = "ASSET-2"


class TestAssetDelegation:

    def test_set_node_choice(self, asset_vuoto):
        asset_vuoto.set_node_choice("REQ-001", "n1", True)
        evidence = asset_vuoto.proprieties.get_evidence("REQ-001")
        assert evidence.node_choices["n1"] is True

    def test_set_justification(self, asset_vuoto):
        asset_vuoto.set_justification("REQ-001", "test")
        evidence = asset_vuoto.proprieties.get_evidence("REQ-001")
        assert evidence.justification == "test"

    def test_set_node_choice_then_justification_preserves_both(self, asset_vuoto):
        asset_vuoto.set_node_choice("REQ-001", "n1", True)
        asset_vuoto.set_justification("REQ-001", "giustificazione")
        evidence = asset_vuoto.proprieties.get_evidence("REQ-001")
        assert evidence.node_choices["n1"] is True
        assert evidence.justification == "giustificazione"


class TestAssetUpdateAnagraphic:

    def test_update_name(self, asset_vuoto):
        new_asset = asset_vuoto.update_anagraphic(name="Nuovo")
        assert new_asset.anagraphic.name == "Nuovo"
        assert asset_vuoto.anagraphic.name == "Network Interface"

    def test_update_type(self, asset_vuoto):
        new_asset = asset_vuoto.update_anagraphic(asset_type=AssetType.SECURITY)
        assert new_asset.anagraphic.asset_type == AssetType.SECURITY

    def test_update_description(self, asset_vuoto):
        new_asset = asset_vuoto.update_anagraphic(description="Nuova descrizione")
        assert new_asset.anagraphic.description == "Nuova descrizione"

    def test_update_partial_preserves(self, asset_vuoto):
        new_asset = asset_vuoto.update_anagraphic(name="Nuovo")
        assert new_asset.anagraphic.description == asset_vuoto.anagraphic.description
        assert new_asset.anagraphic.asset_type == asset_vuoto.anagraphic.asset_type

    def test_update_preserves_proprieties(self, asset_con_evidence):
        new_asset = asset_con_evidence.update_anagraphic(name="Nuovo")
        assert new_asset.proprieties is asset_con_evidence.proprieties

    def test_update_none_noop(self, asset_vuoto):
        new_asset = asset_vuoto.update_anagraphic()
        assert new_asset.anagraphic.name == asset_vuoto.anagraphic.name