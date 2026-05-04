import pytest
from types import MappingProxyType
from core.domain.evaluation_object.asset import AssetEvidence


scenari_iniziali = [
    AssetEvidence(requirement_id="REQ-001"),
    AssetEvidence(requirement_id="REQ-001", node_choices=MappingProxyType({"n-base": True})),
    AssetEvidence(requirement_id="REQ-001", justification="Già giustificata"),
]


@pytest.fixture(params=scenari_iniziali)
def evidence_dinamica(request):
    return request.param


class TestAssetEvidenceImmutability:

    @pytest.mark.requirement("REQ-ENG-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_cannot_set_attributes(self):
        evidence = AssetEvidence(requirement_id="REQ-001")
        with pytest.raises(AttributeError):
            evidence.requirement_id = "REQ-002"

    @pytest.mark.requirement("REQ-ENG-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_cannot_set_justification(self):
        evidence = AssetEvidence(requirement_id="REQ-001")
        with pytest.raises(AttributeError):
            evidence.justification = "nuova"

    @pytest.mark.requirement("REQ-ENG-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_node_choices_not_mutatable(self):
        evidence = AssetEvidence(requirement_id="REQ-001", node_choices=MappingProxyType({"n1": True}))
        with pytest.raises(TypeError):
            evidence.node_choices["n2"] = False


class TestAssetEvidenceWithMethods:

    @pytest.mark.requirement("REQ-ENG-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_with_justification_returns_new_instance(self, evidence_dinamica):
        modified = evidence_dinamica.with_justification("Nuova Giustificazione")
        assert modified is not evidence_dinamica
        assert modified.justification == "Nuova Giustificazione"
        assert modified.node_choices == evidence_dinamica.node_choices

    @pytest.mark.requirement("REQ-ENG-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_with_node_choice_returns_new_instance(self, evidence_dinamica):
        modified = evidence_dinamica.with_node_choice("n-nuovo", False)
        assert modified is not evidence_dinamica
        assert modified.node_choices["n-nuovo"] is False
        assert modified.justification == evidence_dinamica.justification

    @pytest.mark.requirement("REQ-ENG-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_with_node_choice_overwrites_existing_key(self):
        original = AssetEvidence(
            requirement_id="REQ-001",
            node_choices=MappingProxyType({"n1": True}),
        )
        modified = original.with_node_choice("n1", False)
        assert modified.node_choices["n1"] is False
        assert original.node_choices["n1"] is True

    @pytest.mark.requirement("REQ-ENG-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_chaining(self):
        evidence = (
            AssetEvidence(requirement_id="REQ-001")
            .with_node_choice("n1", True)
            .with_node_choice("n2", False)
            .with_justification("Completo")
        )
        assert evidence.node_choices["n1"] is True
        assert evidence.node_choices["n2"] is False
        assert evidence.justification == "Completo"