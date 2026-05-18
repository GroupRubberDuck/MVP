import pytest
from types import MappingProxyType
from core.domain.evaluation_object.asset import AssetEvidence


scenari_iniziali = [
    AssetEvidence(requirement_id="REQ-001"),
    AssetEvidence(
        requirement_id="REQ-001", node_choices=MappingProxyType({"n-base": True})
    ),
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
        """
        Dato un oggetto AssetEvidence regolarmente istanziato (Given),
        quando si tenta di riassegnare il suo identificatore di requisito (When),
        allora il sistema deve impedire la modifica sollevando un AttributeError (Then).
        """
        evidence = AssetEvidence(requirement_id="REQ-001")
        with pytest.raises(AttributeError):
            evidence.requirement_id = "REQ-002"

    @pytest.mark.requirement("REQ-ENG-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_cannot_set_justification(self):
        """
        Dato un oggetto AssetEvidence (Given),
        quando si tenta di sovrascrivere direttamente la proprietà della giustificazione (When),
        allora il dominio deve proteggere l'integrità dell'oggetto bloccando l'azione con un AttributeError (Then).
        """
        evidence = AssetEvidence(requirement_id="REQ-001")
        with pytest.raises(AttributeError):
            evidence.justification = "nuova"

    @pytest.mark.requirement("REQ-ENG-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_node_choices_not_mutatable(self):
        """
        Dato un oggetto AssetEvidence contenente una mappa di scelte per i nodi (Given),
        quando si tenta di mutare il dizionario interno aggiungendo una nuova chiave (When),
        allora deve essere sollevato un TypeError poiché la mappa è protetta da un MappingProxyType (Then).
        """
        evidence = AssetEvidence(
            requirement_id="REQ-001", node_choices=MappingProxyType({"n1": True})
        )
        with pytest.raises(TypeError):
            evidence.node_choices["n2"] = False


class TestAssetEvidenceWithMethods:
    @pytest.mark.requirement("REQ-ENG-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_with_justification_returns_new_instance(self, evidence_dinamica):
        """
        Dati diversi scenari iniziali di un'evidenza (Given),
        quando viene aggiornata la giustificazione tramite il metodo dedicato (When),
        allora il sistema deve restituire una nuova istanza distinta con il valore aggiornato, preservando le scelte precedenti (Then).
        """
        modified = evidence_dinamica.with_justification("Nuova Giustificazione")
        assert modified is not evidence_dinamica
        assert modified.justification == "Nuova Giustificazione"
        assert modified.node_choices == evidence_dinamica.node_choices

    @pytest.mark.requirement("REQ-ENG-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_with_node_choice_returns_new_instance(self, evidence_dinamica):
        """
        Dati diversi stati iniziali di un'evidenza (Given),
        quando viene aggiunta una nuova scelta per un nodo tramite il metodo dedicato (When),
        allora deve essere prodotta una nuova istanza che include la nuova scelta e mantiene la giustificazione originale (Then).
        """
        modified = evidence_dinamica.with_node_choice("n-nuovo", False)
        assert modified is not evidence_dinamica
        assert modified.node_choices["n-nuovo"] is False
        assert modified.justification == evidence_dinamica.justification

    @pytest.mark.requirement("REQ-ENG-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_with_node_choice_overwrites_existing_key(self):
        """
        Data un'evidenza che contiene già una scelta per uno specifico nodo (Given),
        quando viene sottomessa una nuova scelta per lo stesso identificatore di nodo (When),
        allora la nuova istanza restituita deve contenere il valore sovrascritto, lasciando inalterata l'istanza di partenza (Then).
        """
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
        """
        Dato il pattern di creazione fluido (fluent interface) del Value Object (Given),
        quando vengono concatenate più chiamate di aggiornamento per nodi e giustificazione (When),
        allora l'istanza finale risultante deve consolidare correttamente tutte le trasformazioni effettuate nella catena (Then).
        """
        evidence = (
            AssetEvidence(requirement_id="REQ-001")
            .with_node_choice("n1", True)
            .with_node_choice("n2", False)
            .with_justification("Completo")
        )
        assert evidence.node_choices["n1"] is True
        assert evidence.node_choices["n2"] is False
        assert evidence.justification == "Completo"
