import pytest


from core.domain.device import Answer


class TestAnswerCreation:
    """Test di creazione della classe Answer"""

    @pytest.mark.requirement("REQ-DEV-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_answer_default_creation(self):
        """
        Un Answer creato senza parametri ha giustificazione vuota
        e nessuna risposta.
        """
        answer = Answer()
        assert answer.get_justification() == ""
        assert answer.get_answers() == {}

    @pytest.mark.requirement("REQ-DEV-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_answer_creation_with_justification(self):
        """
        Un Answer può essere creato con una giustificazione iniziale.
        """
        answer = Answer(justification="Non applicabile al contesto")
        assert answer.get_justification() == "Non applicabile al contesto"

    @pytest.mark.requirement("REQ-DEV-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_answer_creation_with_answers(self):
        """
        Un Answer può essere creato con risposte iniziali.
        """
        initial = {"node-1": True, "node-2": False}
        answer = Answer(answers=initial)
        assert answer.get_answer("node-1") is True
        assert answer.get_answer("node-2") is False


class TestAnswerSetAnswer:
    """Test di modifica delle risposte in Answer"""

    @pytest.mark.requirement("REQ-DEV-02")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_set_answer_adds_new_entry(self):
        """
        set_answer aggiunge una nuova risposta se la chiave non esiste.
        """
        answer = Answer()
        answer.set_answer("node-1", True)
        assert answer.get_answer("node-1") is True

    @pytest.mark.requirement("REQ-DEV-02")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_set_answer_overwrites_existing(self):
        """
        set_answer sovrascrive una risposta esistente.
        """
        answer = Answer(answers={"node-1": True})
        answer.set_answer("node-1", False)
        assert answer.get_answer("node-1") is False

    @pytest.mark.requirement("REQ-DEV-02")
    @pytest.mark.priority("medium")
    @pytest.mark.type("unità")
    def test_set_answer_does_not_affect_others(self):
        """
        Modificare una risposta non altera le altre.
        """
        answer = Answer(answers={"node-1": True, "node-2": False})
        answer.set_answer("node-1", False)
        assert answer.get_answer("node-2") is False


class TestAnswerSetJustification:
    """Test di modifica della giustificazione in Answer"""

    @pytest.mark.requirement("REQ-DEV-03")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_set_justification(self):
        """
        set_justification aggiorna il testo della giustificazione.
        """
        answer = Answer()
        answer.set_justification("Conforme allo standard ISO 27001")
        assert answer.get_justification() == "Conforme allo standard ISO 27001"

    @pytest.mark.requirement("REQ-DEV-03")
    @pytest.mark.priority("medium")
    @pytest.mark.type("unità")
    def test_set_justification_overwrites(self):
        """
        set_justification sovrascrive la giustificazione precedente.
        """
        answer = Answer(justification="Vecchia motivazione")
        answer.set_justification("Nuova motivazione")
        assert answer.get_justification() == "Nuova motivazione"


class TestAnswerEncapsulation:
    """Test di protezione dello stato interno di Answer"""

    @pytest.mark.requirement("REQ-DEV-04")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_get_answers_returns_copy(self):
        """
        get_answers restituisce una copia del dizionario.
        Modifiche alla copia non alterano lo stato interno.
        """
        answer = Answer(answers={"node-1": True})
        external = answer.get_answers()
        external["node-1"] = False
        assert answer.get_answer("node-1") is True

    @pytest.mark.requirement("REQ-DEV-04")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_constructor_does_not_hold_reference(self):
        """
        Il dizionario passato al costruttore viene copiato.
        Modifiche all'originale non alterano lo stato interno.
        """
        original = {"node-1": True}
        answer = Answer(answers=original)
        original["node-1"] = False
        assert answer.get_answer("node-1") is True