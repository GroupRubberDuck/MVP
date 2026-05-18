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
        """
        Data l'inizializzazione di una nuova evidenza per un requisito (Given),
        quando viene creata senza parametri opzionali (When),
        allora la mappa delle scelte dei nodi deve risultare vuota e la giustificazione una stringa vuota (Then).
        """
        evidence = AssetEvidence(requirement_id="REQ-001")
        assert evidence.node_choices == MappingProxyType({})
        assert evidence.justification == ""

    def test_with_node_choice_returns_new_instance(self):
        """
        Data un'evidenza esistente (Given),
        quando viene aggiunta una nuova scelta per un nodo (When),
        allora deve restituire una nuova istanza immutabile aggiornata, lasciando intatta l'evidenza originale (Then).
        """
        original = AssetEvidence(requirement_id="REQ-001")
        updated = original.with_node_choice("n1", True)
        assert updated is not original
        assert updated.node_choices["n1"] is True
        assert "n1" not in original.node_choices

    def test_with_node_choice_preserves_justification(self):
        """
        Data un'evidenza contenente già una giustificazione (Given),
        quando viene aggiunta una scelta nodo generando una nuova istanza (When),
        allora la nuova istanza deve preservare la giustificazione registrata in precedenza (Then).
        """
        original = AssetEvidence(requirement_id="REQ-001", justification="test")
        updated = original.with_node_choice("n1", True)
        assert updated.justification == "test"

    def test_with_justification_returns_new_instance(self):
        """
        Data un'evidenza esistente contenente scelte pregresse (Given),
        quando viene aggiornata la giustificazione (When),
        allora deve restituire una nuova istanza con il testo aggiornato, preservando le scelte della precedente (Then).
        """
        original = AssetEvidence(
            requirement_id="REQ-001",
            node_choices=MappingProxyType({"n1": True}),
        )
        updated = original.with_justification("nuova")
        assert updated is not original
        assert updated.justification == "nuova"
        assert updated.node_choices["n1"] is True

    def test_frozen(self):
        """
        Data un'istanza di evidenza appena creata (Given),
        quando si tenta di modificarne direttamente un attributo bypassando i metodi costruttori (When),
        allora il sistema deve bloccare l'operazione sollevando un AttributeError poiché la classe è immutabile (frozen) (Then).
        """
        evidence = AssetEvidence(requirement_id="REQ-001")
        with pytest.raises(AttributeError):
            evidence.justification = "modifica"


# ── AssetProprieties ──


class TestAssetProprieties:
    def test_empty_by_default(self):
        """
        Data l'inizializzazione del gestore delle proprietà di un asset (Given),
        quando viene istanziato senza parametri (When),
        allora il dizionario delle evidenze associato deve risultare vuoto (Then).
        """
        proprieties = AssetProprieties()
        assert len(proprieties.evidences) == 0

    def test_set_node_choice_creates_evidence_automatically(self):
        """
        Dato un gestore di proprietà ancora vuoto (Given),
        quando viene registrata la scelta di un nodo associata a un requisito (When),
        allora l'evidenza per quel requisito deve essere istanziata automaticamente e popolata con la scelta (Then).
        """
        proprieties = AssetProprieties()
        proprieties.set_node_choice("REQ-001", "n1", True)
        evidence = proprieties.get_evidence("REQ-001")
        assert evidence is not None
        assert evidence.node_choices["n1"] is True

    def test_set_node_choice_preserves_existing(self):
        """
        Dato un gestore di proprietà che contiene già una scelta nodo per un requisito (Given),
        quando viene aggiunta una seconda scelta per un nodo differente dello stesso requisito (When),
        allora l'evidenza aggiornata deve includere entrambe le scelte senza perdite di dati (Then).
        """
        proprieties = AssetProprieties()
        proprieties.set_node_choice("REQ-001", "n1", True)
        proprieties.set_node_choice("REQ-001", "n2", False)
        evidence = proprieties.get_evidence("REQ-001")
        assert evidence.node_choices["n1"] is True
        assert evidence.node_choices["n2"] is False

    def test_set_justification_creates_evidence_automatically(self):
        """
        Dato un gestore di proprietà vuoto (Given),
        quando viene salvata una giustificazione per un requisito (When),
        allora l'evidenza per quel requisito deve essere creata in automatico contenendo la corretta giustificazione (Then).
        """
        proprieties = AssetProprieties()
        proprieties.set_justification("REQ-001", "giustificazione")
        evidence = proprieties.get_evidence("REQ-001")
        assert evidence is not None
        assert evidence.justification == "giustificazione"

    def test_set_justification_preserves_node_choices(self):
        """
        Dato un gestore di proprietà che possiede delle scelte nodo salvate per un requisito (Given),
        quando viene inserita una giustificazione per lo stesso (When),
        allora l'evidenza aggiornata deve mantenere le scelte pregresse affiancandole al nuovo testo (Then).
        """
        proprieties = AssetProprieties()
        proprieties.set_node_choice("REQ-001", "n1", True)
        proprieties.set_justification("REQ-001", "giustificazione")
        evidence = proprieties.get_evidence("REQ-001")
        assert evidence.node_choices["n1"] is True
        assert evidence.justification == "giustificazione"

    def test_get_evidence_missing_returns_none(self):
        """
        Dato un gestore di proprietà (Given),
        quando si tenta di estrarre un'evidenza per un requisito non valutato (When),
        allora il metodo deve gestire l'assenza restituendo None in modo sicuro (Then).
        """
        proprieties = AssetProprieties()
        assert proprieties.get_evidence("REQ-999") is None

    def test_evidences_immutable_view(self):
        """
        Dato un gestore di proprietà popolato (Given),
        quando si tenta di manipolare direttamente il dizionario restituito dalla property 'evidences' (When),
        allora il sistema deve bloccare l'azione con un TypeError poiché è esposta come MappingProxyType di sola lettura (Then).
        """
        proprieties = AssetProprieties()
        proprieties.set_node_choice("REQ-001", "n1", True)
        with pytest.raises(TypeError):
            proprieties.evidences["REQ-002"] = AssetEvidence(requirement_id="REQ-002")

    def test_init_with_existing_evidences(self):
        """
        Dato un dizionario di evidenze preesistente (Given),
        quando il gestore delle proprietà viene inizializzato passandoglielo nel costruttore (When),
        allora i dati devono essere correttamente inglobati e resi disponibili (Then).
        """
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
        """
        Dati dei parametri anagrafici validi (Given),
        quando un Asset viene istanziato senza fornire proprietà valutative (When),
        allora l'entità deve essere creata correttamente con un gestore di proprietà inizializzato e vuoto (Then).
        """
        assert asset_vuoto.id == "ASSET-1"
        assert len(asset_vuoto.proprieties.evidences) == 0

    def test_create_with_proprieties(self, asset_con_evidence):
        """
        Dato un set di proprietà contenente valutazioni (Given),
        quando l'Asset viene istanziato integrandole (When),
        allora l'entità deve esporre correttamente le evidenze precaricate (Then).
        """
        evidence = asset_con_evidence.proprieties.get_evidence("REQ-001")
        assert evidence is not None
        assert evidence.node_choices["n1"] is True

    def test_frozen_id(self, asset_vuoto):
        """
        Dato un Asset regolarmente istanziato (Given),
        quando si tenta di riassegnare direttamente il suo ID univoco (When),
        allora il dominio deve prevenire l'azione sollevando un AttributeError a tutela dell'immutabilità della chiave (Then).
        """
        with pytest.raises(AttributeError):
            asset_vuoto.id = "ASSET-2"


class TestAssetDelegation:
    def test_set_node_choice(self, asset_vuoto):
        """
        Dato un Asset (Given),
        quando viene richiamato il metodo per impostare la scelta di un nodo (When),
        allora l'Asset deve delegare in modo trasparente l'operazione al suo gestore interno delle proprietà (Then).
        """
        asset_vuoto.set_node_choice("REQ-001", "n1", True)
        evidence = asset_vuoto.proprieties.get_evidence("REQ-001")
        assert evidence.node_choices["n1"] is True

    def test_set_justification(self, asset_vuoto):
        """
        Dato un Asset (Given),
        quando viene invocato il metodo per registrare una giustificazione (When),
        allora l'Asset deve instradare correttamente l'informazione aggiornando le proprietà interne (Then).
        """
        asset_vuoto.set_justification("REQ-001", "test")
        evidence = asset_vuoto.proprieties.get_evidence("REQ-001")
        assert evidence.justification == "test"

    def test_set_node_choice_then_justification_preserves_both(self, asset_vuoto):
        """
        Dato un Asset valutato iterativamente (Given),
        quando vengono registrate in sequenza una scelta nodo e una giustificazione sullo stesso requisito (When),
        allora l'Asset, delegando alle proprietà, deve consolidare entrambe le informazioni mantenendole coerenti (Then).
        """
        asset_vuoto.set_node_choice("REQ-001", "n1", True)
        asset_vuoto.set_justification("REQ-001", "giustificazione")
        evidence = asset_vuoto.proprieties.get_evidence("REQ-001")
        assert evidence.node_choices["n1"] is True
        assert evidence.justification == "giustificazione"


class TestAssetUpdateAnagraphic:
    def test_update_name(self, asset_vuoto):
        """
        Dato un Asset esistente (Given),
        quando si richiede l'aggiornamento del suo nome anagrafico (When),
        allora deve essere restituita una nuova istanza clone recante il nuovo nome, lasciando inalterato l'originale (Then).
        """
        new_asset = asset_vuoto.update_anagraphic(name="Nuovo")
        assert new_asset.anagraphic.name == "Nuovo"
        assert asset_vuoto.anagraphic.name == "Network Interface"

    def test_update_type(self, asset_vuoto):
        """
        Dato un Asset esistente (Given),
        quando viene aggiornata la tipologia nell'anagrafica (When),
        allora la nuova istanza restituita deve riflettere il nuovo AssetType (Then).
        """
        new_asset = asset_vuoto.update_anagraphic(asset_type=AssetType.SECURITY)
        assert new_asset.anagraphic.asset_type == AssetType.SECURITY

    def test_update_description(self, asset_vuoto):
        """
        Dato un Asset esistente (Given),
        quando viene aggiornata la sua descrizione tecnica (When),
        allora la nuova istanza creata deve contenere il testo descrittivo aggiornato (Then).
        """
        new_asset = asset_vuoto.update_anagraphic(description="Nuova descrizione")
        assert new_asset.anagraphic.description == "Nuova descrizione"

    def test_update_partial_preserves(self, asset_vuoto):
        """
        Dato un Asset esistente (Given),
        quando si invoca l'aggiornamento parziale fornendo solo un sottoinsieme dei campi anagrafici (es. solo il nome) (When),
        allora l'entità clonata deve ereditare i valori originali per tutti i campi non esplicitamente modificati (Then).
        """
        new_asset = asset_vuoto.update_anagraphic(name="Nuovo")
        assert new_asset.anagraphic.description == asset_vuoto.anagraphic.description
        assert new_asset.anagraphic.asset_type == asset_vuoto.anagraphic.asset_type

    def test_update_preserves_proprieties(self, asset_con_evidence):
        """
        Dato un Asset contenente valutazioni ed evidenze pregresse (Given),
        quando viene prodotta una nuova istanza per aggiornarne l'anagrafica (When),
        allora la nuova istanza deve preservare i riferimenti esatti al contenitore delle proprietà originale (Then).
        """
        new_asset = asset_con_evidence.update_anagraphic(name="Nuovo")
        assert new_asset.proprieties is asset_con_evidence.proprieties

    def test_update_none_noop(self, asset_vuoto):
        """
        Dato un Asset (Given),
        quando il metodo di aggiornamento viene invocato senza passare alcun nuovo parametro anagrafico (When),
        allora la nuova istanza creata deve essere un clone con anagrafica identica all'originale (Then).
        """
        new_asset = asset_vuoto.update_anagraphic()
        assert new_asset.anagraphic.name == asset_vuoto.anagraphic.name
