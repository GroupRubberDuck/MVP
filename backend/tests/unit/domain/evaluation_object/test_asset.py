import pytest
from types import MappingProxyType
from core.domain.evaluation_object.answer import Answer
from core.domain.evaluation_object.asset import Asset
from core.domain.evaluation_object.asset_type import AssetType
from core.domain.evaluation_object.exceptions import (
    AnswerNotFoundError,
    RequirementAlreadyExistsError,
)


# ── Fixtures ──

@pytest.fixture
def asset_vuoto():
    return Asset.create(
        asset_id="ASSET-1", name="Network Interface",
        asset_type=AssetType.NETWORK, description="Ethernet controller",
    )


@pytest.fixture
def asset_con_answer():
    return Asset.create(
        asset_id="ASSET-1", name="Network Interface",
        asset_type=AssetType.NETWORK, description="Ethernet controller",
        answers=[Answer(requirement_id="REQ-001")],
    )


scenari_answer = [
    Answer(requirement_id="REQ-001"),
    Answer(requirement_id="REQ-001", node_choices=MappingProxyType({"n-base": True})),
    Answer(requirement_id="REQ-001", justification="Già giustificata"),
]


@pytest.fixture(params=scenari_answer)
def answer_dinamica(request):
    return request.param


# ── Creazione ──

class TestAssetCreation:

    def test_create_empty(self, asset_vuoto):
        assert asset_vuoto.id == "ASSET-1"
        assert len(asset_vuoto.answers) == 0

    def test_create_with_answers(self):
        answers = [Answer(requirement_id="REQ-001"), Answer(requirement_id="REQ-002")]
        asset = Asset.create(
            asset_id="ASSET-1", name="Test",
            asset_type=AssetType.NETWORK, description="Test",
            answers=answers,
        )
        assert len(asset.answers) == 2
        assert "REQ-001" in asset.answers
        assert "REQ-002" in asset.answers


# ── Gestione Answer ──

class TestAssetAnswerManagement:

    def test_add_answer(self, asset_vuoto, answer_dinamica):
        asset_vuoto.add_answer(answer_dinamica)
        stored = asset_vuoto.get_answer(answer_dinamica.requirement_id)
        assert stored.requirement_id == answer_dinamica.requirement_id
        assert stored.node_choices == answer_dinamica.node_choices
        assert stored.justification == answer_dinamica.justification

    def test_add_duplicate_raises(self, asset_con_answer):
        with pytest.raises(RequirementAlreadyExistsError):
            asset_con_answer.add_answer(Answer(requirement_id="REQ-001"))

    def test_get_missing_answer(self, asset_vuoto):
        assert asset_vuoto.get_answer("REQ-999") is None

    def test_answers_immutable_view(self, asset_con_answer):
        with pytest.raises(TypeError):
            asset_con_answer.answers["REQ-002"] = Answer(requirement_id="REQ-002")


# ── set_node_choice e set_justification ──

class TestAssetNodeChoiceAndJustification:

    def test_set_node_choice(self, asset_vuoto, answer_dinamica):
        """Parametrizzato: verifica su ogni tipo di Answer iniziale."""
        asset_vuoto.add_answer(answer_dinamica)
        asset_vuoto.set_node_choice("REQ-001", "n-nuovo", True)
        updated = asset_vuoto.get_answer("REQ-001")
        assert updated.node_choices["n-nuovo"] is True
        # preserva la justification originale
        assert updated.justification == answer_dinamica.justification

    def test_set_justification(self, asset_vuoto, answer_dinamica):
        """Parametrizzato: verifica su ogni tipo di Answer iniziale."""
        asset_vuoto.add_answer(answer_dinamica)
        asset_vuoto.set_justification("REQ-001", "Nuova giustificazione")
        updated = asset_vuoto.get_answer("REQ-001")
        assert updated.justification == "Nuova giustificazione"
        # preserva le node_choices originali
        assert updated.node_choices == answer_dinamica.node_choices

    def test_set_node_choice_missing_raises(self, asset_vuoto):
        with pytest.raises(AnswerNotFoundError):
            asset_vuoto.set_node_choice("REQ-999", "n1", True)

    def test_set_justification_missing_raises(self, asset_vuoto):
        with pytest.raises(AnswerNotFoundError):
            asset_vuoto.set_justification("REQ-999", "test")


# ── update_info ──

class TestAssetUpdateInfo:

    def test_update_name(self, asset_vuoto):
        asset_vuoto.update_info(name="Nuovo")
        assert asset_vuoto.name == "Nuovo"

    def test_update_type(self, asset_vuoto):
        asset_vuoto.update_info(asset_type=AssetType.SECURITY)
        assert asset_vuoto.asset_type == AssetType.SECURITY

    def test_update_description(self, asset_vuoto):
        asset_vuoto.update_info(description="Nuova descrizione")
        assert asset_vuoto.description == "Nuova descrizione"

    def test_update_partial_preserves(self, asset_vuoto):
        orig_desc = asset_vuoto.description
        orig_type = asset_vuoto.asset_type
        asset_vuoto.update_info(name="Nuovo")
        assert asset_vuoto.description == orig_desc
        assert asset_vuoto.asset_type == orig_type

    def test_update_none_noop(self, asset_vuoto):
        orig_name = asset_vuoto.name
        asset_vuoto.update_info()
        assert asset_vuoto.name == orig_name