import pytest

from core.domain.evaluation_object.answer import Answer

class TestAnswer:
        """Test di creazione della classe Answer"""
        @pytest.mark.requirement("REQ-DEV-01")
        @pytest.mark.priority("high")
        @pytest.mark.type("unità")
        def test_answer_creation(self):
                """
                Un Answer può essere creato solo con il codice del requisito.
                """
                answer = Answer("acm-1")
                assert answer.requirement_id == "acm-1"
                assert answer.justification == ""
                assert len(answer.node_choices) == 0

        @pytest.mark.requirement("REQ-DEV-01")
        @pytest.mark.priority("high")
        @pytest.mark.type("unità")
        def test_answer_creation_with_initial_data(self):
            """
            Un Answer può essere creato con dati iniziali.
            """
            initial = {"node-1": True, "node-2": False}
            answer = Answer("acm-1", justification="Non applicabile al contesto", node_choices=initial)
            assert answer.requirement_id == "acm-1"
            assert answer.justification == "Non applicabile al contesto"
            assert answer.node_choices["node-1"] is True
            assert answer.node_choices["node-2"] is False

        @pytest.mark.requirement("REQ-DEV-01")
        @pytest.mark.priority("high")
        @pytest.mark.type("unità")
        def test_answer_creation_with_empty_node_choices(self):
            """
            Un Answer può essere creato con un dizionario vuoto di node_choices.
            """
            answer = Answer("acm-1", justification="Non applicabile al contesto", node_choices={})
            assert answer.requirement_id == "acm-1"
            assert answer.justification == "Non applicabile al contesto"
            assert len(answer.node_choices) == 0


        @pytest.mark.requirement("REQ-DEV-01")
        @pytest.mark.priority("high")
        @pytest.mark.type("unità")
        def test_answer_creation_with_none_node_choices(self):
            """
            Un Answer può essere creato con node_choices impostato a None.
            """
            answer = Answer("acm-1", justification="Non applicabile al contesto", node_choices=None)
            assert answer.requirement_id == "acm-1"
            assert answer.justification == "Non applicabile al contesto"
            assert len(answer.node_choices) == 0

        @pytest.mark.requirement("REQ-DEV-01")
        @pytest.mark.priority("high")
        @pytest.mark.type("unità")
        def test_setter_methods(self):
            """
            I setter di Answer funzionano correttamente.
            """
            answer = Answer("acm-1")
            answer.set_justification("Conforme allo standard")
            answer.set_node_choice("node-1", True)
            assert answer.justification == "Conforme allo standard"
            assert answer.node_choices["node-1"] is True

        @pytest.mark.requirement("REQ-DEV-01")
        @pytest.mark.priority("high")
        @pytest.mark.type("unità")
        def test_create_snapshot(self):
            """
            Il metodo create_snapshot restituisce un SnapshotAnswer con i dati corretti.
            """
            answer = Answer("acm-1", justification="Non applicabile al contesto", node_choices={"node-1": True})
            snapshot = answer.create_snapshot()
            assert snapshot.requirement_id == "acm-1"
            assert snapshot.justification == "Non applicabile al contesto"
            assert snapshot.node_choices["node-1"] is True

        @pytest.mark.requirement("REQ-DEV-01")
        @pytest.mark.priority("high")
        @pytest.mark.type("unità")
        def test_node_choices_immutability(self):
            """
            Il dizionario node_choices restituito da Answer è immutabile.
            """
            answer = Answer("acm-1", node_choices={"node-1": True})
            node_choices = answer.node_choices
            with pytest.raises(TypeError):
                node_choices["node-2"] = False

