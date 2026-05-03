import pytest
from types import MappingProxyType
from core.domain.evaluation_object.answer import Answer

scenari_iniziali = [
    Answer(requirement_id="REQ-001"),
    Answer(requirement_id="REQ-001", node_choices=MappingProxyType({"n-base": True})),
    Answer(requirement_id="REQ-001", justification="Già giustificata"),
]

@pytest.fixture(params=scenari_iniziali)
def answer_dinamica(request):
    return request.param


class TestAnswerImmutability:
    @pytest.mark.requirement("REQ-ENG-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")

    def test_cannot_set_attributes(self):
        answer = Answer(requirement_id="REQ-001")
        with pytest.raises(AttributeError):
            answer.requirement_id = "REQ-002"

    @pytest.mark.requirement("REQ-ENG-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")

    def test_cannot_set_justification(self):
        answer = Answer(requirement_id="REQ-001")
        with pytest.raises(AttributeError):
            answer.justification = "nuova"

    @pytest.mark.requirement("REQ-ENG-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")

    def test_node_choices_not_mutatable(self):
        answer = Answer(requirement_id="REQ-001", node_choices=MappingProxyType({"n1": True}))
        with pytest.raises(TypeError):
            answer.node_choices["n2"] = False


class TestAnswerWithMethods:
            
    @pytest.mark.requirement("REQ-ENG-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")

    def test_with_justification_returns_new_instance(self, answer_dinamica):
        modified = answer_dinamica.with_justification("Nuova Giustificazione")
        assert modified is not answer_dinamica
        assert modified.justification == "Nuova Giustificazione"
        assert modified.node_choices == answer_dinamica.node_choices
            
    @pytest.mark.requirement("REQ-ENG-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_with_node_choice_returns_new_instance(self, answer_dinamica):
        modified = answer_dinamica.with_node_choice("n-nuovo", False)
        assert modified is not answer_dinamica
        assert modified.node_choices["n-nuovo"] is False
        assert modified.justification == answer_dinamica.justification

    @pytest.mark.requirement("REQ-ENG-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_with_node_choice_overwrites_existing_key(self):
        original = Answer(
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
        answer = (
            Answer(requirement_id="REQ-001")
            .with_node_choice("n1", True)
            .with_node_choice("n2", False)
            .with_justification("Completo")
        )
        assert answer.node_choices["n1"] is True
        assert answer.node_choices["n2"] is False
        assert answer.justification == "Completo"