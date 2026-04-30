import pytest

from core.domain.evaluation_object.answer import Answer
from core.domain.evaluation_object.asset import Asset
from core.domain.evaluation_object.asset_type import AssetType
from core.domain.evaluation_object.device import Device
from core.domain.evaluation_object.exceptions import (
    DuplicateAssetError,
    AssetNotFoundError,
    RequirementNotFoundError,
    RequirementAlreadyExistsError,
)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def answer() -> Answer:
    return Answer.create("req-1", justification="Giustificazione", node_choices={"node-1": True, "node-2": False})


@pytest.fixture
def asset() -> Asset:
    return Asset("asset-1", "Asset 1", AssetType.SECURITY, "Descrizione asset")


@pytest.fixture
def asset_with_answers() -> Asset:
    return Asset.create(
        asset_id="asset-1",
        name="Asset 1",
        asset_type=AssetType.SECURITY,
        description="Descrizione asset",
        answers=[
            Answer.create("req-1", justification="Prima", node_choices={"node-1": True}),
            Answer.create("req-2", justification="Seconda", node_choices={"node-2": False}),
        ],
    )


@pytest.fixture
def device() -> Device:
    return Device("d-1", "std-1", "Device 1", "Android", "Descrizione device")


@pytest.fixture
def device_with_asset(asset_with_answers) -> Device:
    d = Device("d-1", "std-1", "Device 1", "Android", "Descrizione device")
    d.add_asset(asset_with_answers)
    return d


# ─────────────────────────────────────────────────────────────────────────────
# Answer
# ─────────────────────────────────────────────────────────────────────────────

class TestAnswer:

    # --- creazione ---

    @pytest.mark.requirement("REQ-ANS-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_init_minimal(self):
        """Answer creata con solo requirement_id ha justification vuota e nessun node_choice."""
        answer = Answer("req-1")
        assert answer.requirement_id == "req-1"
        assert answer.justification == ""
        assert len(answer.node_choices) == 0

    @pytest.mark.requirement("REQ-ANS-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_create_with_all_fields(self):
        """Answer.create popola correttamente tutti i campi."""
        answer = Answer.create("req-1", justification="Testo", node_choices={"node-1": True})
        assert answer.requirement_id == "req-1"
        assert answer.justification == "Testo"
        assert answer.node_choices["node-1"] is True

    @pytest.mark.requirement("REQ-ANS-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_create_with_none_node_choices(self):
        """Answer.create con node_choices=None produce un dizionario vuoto."""
        answer = Answer.create("req-1", node_choices=None)
        assert len(answer.node_choices) == 0

    @pytest.mark.requirement("REQ-ANS-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_create_isolates_input_dict(self):
        """
        Modificare il dizionario passato a create non deve alterare
        lo stato interno di Answer.
        """
        initial = {"node-1": True}
        answer = Answer.create("req-1", node_choices=initial)

        initial["node-1"] = False

        assert answer.node_choices["node-1"] is True

    # --- set_node_choice ---

    @pytest.mark.requirement("REQ-ANS-02")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_set_node_choice_adds_new_node(self):
        """set_node_choice aggiunge un nodo non esistente."""
        answer = Answer("req-1")
        answer.set_node_choice("node-1", True)
        assert answer.node_choices["node-1"] is True

    @pytest.mark.requirement("REQ-ANS-02")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_set_node_choice_overwrites_existing(self):
        """set_node_choice sovrascrive il valore di un nodo già presente."""
        answer = Answer.create("req-1", node_choices={"node-1": True})
        answer.set_node_choice("node-1", False)
        assert answer.node_choices["node-1"] is False

    # --- set_justification ---

    @pytest.mark.requirement("REQ-ANS-03")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_set_justification(self):
        """set_justification aggiorna correttamente il testo."""
        answer = Answer("req-1")
        answer.set_justification("Nuovo testo")
        assert answer.justification == "Nuovo testo"

    # --- node_choices property ---

    @pytest.mark.requirement("REQ-ANS-04")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_node_choices_property_is_read_only(self):
        """La property node_choices restituisce un MappingProxyType immutabile."""
        answer = Answer.create("req-1", node_choices={"node-1": True})
        with pytest.raises(TypeError):
            answer.node_choices["node-1"] = False  # type: ignore


# ─────────────────────────────────────────────────────────────────────────────
# Asset
# ─────────────────────────────────────────────────────────────────────────────

class TestAsset:

    # --- creazione ---

    @pytest.mark.requirement("REQ-ASS-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_init_minimal(self):
        """Asset creato con __init__ ha _answers vuoto."""
        asset = Asset("asset-1", "Asset 1", AssetType.SECURITY, "Desc")
        assert asset.id == "asset-1"
        assert asset.name == "Asset 1"
        assert asset.asset_type == AssetType.SECURITY
        assert asset.description == "Desc"
        assert len(asset.answers) == 0

    @pytest.mark.requirement("REQ-ASS-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_create_with_answers(self):
        """Asset.create inserisce le answers iniziali tramite add_answer."""
        asset = Asset.create(
            asset_id="asset-1",
            name="Asset 1",
            asset_type=AssetType.SECURITY,
            description="Desc",
            answers=[
                Answer.create("req-1", node_choices={"node-1": True}),
                Answer.create("req-2", node_choices={"node-2": False}),
            ],
        )
        assert len(asset.answers) == 2
        assert "req-1" in asset.answers
        assert "req-2" in asset.answers

    @pytest.mark.requirement("REQ-ASS-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_create_with_none_answers(self):
        """Asset.create con answers=None produce un Asset senza answers."""
        asset = Asset.create("asset-1", "Asset 1", AssetType.SECURITY, "Desc", answers=None)
        assert len(asset.answers) == 0

    @pytest.mark.requirement("REQ-ASS-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_create_with_duplicate_answers_raises(self):
        """Asset.create con answers duplicate solleva RequirementAlreadyExistsError."""
        with pytest.raises(RequirementAlreadyExistsError):
            Asset.create(
                asset_id="asset-1",
                name="Asset 1",
                asset_type=AssetType.SECURITY,
                description="Desc",
                answers=[Answer("req-1"), Answer("req-1")],
            )

    # --- add_answer ---

    @pytest.mark.requirement("REQ-ASS-02")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_add_answer(self):
        """add_answer inserisce correttamente una nuova Answer."""
        asset = Asset("asset-1", "Asset 1", AssetType.SECURITY, "Desc")
        asset.add_answer(Answer.create("req-1", node_choices={"node-1": True}))
        assert "req-1" in asset.answers
        assert asset.answers["req-1"].node_choices["node-1"] is True

    @pytest.mark.requirement("REQ-ASS-02")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_add_answer_duplicate_raises(self):
        """add_answer solleva RequirementAlreadyExistsError se il requisito esiste già."""
        asset = Asset("asset-1", "Asset 1", AssetType.SECURITY, "Desc")
        asset.add_answer(Answer("req-1"))
        with pytest.raises(RequirementAlreadyExistsError):
            asset.add_answer(Answer("req-1"))

    @pytest.mark.requirement("REQ-ASS-02")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_add_answer_isolates_internal_state(self):
        """
        Modificare l'Answer originale dopo add_answer non deve alterare
        lo stato interno dell'Asset (deepcopy in ingresso).
        """
        asset = Asset("asset-1", "Asset 1", AssetType.SECURITY, "Desc")
        answer = Answer.create("req-1", node_choices={"node-1": True})
        asset.add_answer(answer)

        answer.set_node_choice("node-1", False)

        assert asset.answers["req-1"].node_choices["node-1"] is True

    # --- set_node_choice ---

    @pytest.mark.requirement("REQ-ASS-03")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_set_node_choice(self):
        """set_node_choice aggiorna correttamente il valore di un nodo."""
        asset = Asset.create("asset-1", "Asset 1", AssetType.SECURITY, "Desc",
                             answers=[Answer.create("req-1", node_choices={"node-1": False})])
        asset.set_node_choice("req-1", "node-1", True)
        assert asset.answers["req-1"].node_choices["node-1"] is True

    @pytest.mark.requirement("REQ-ASS-03")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_set_node_choice_nonexistent_requirement_raises(self):
        """set_node_choice solleva RequirementNotFoundError se il requisito non esiste."""
        asset = Asset("asset-1", "Asset 1", AssetType.SECURITY, "Desc")
        with pytest.raises(RequirementNotFoundError):
            asset.set_node_choice("req-inesistente", "node-1", True)

    # --- set_justification ---

    @pytest.mark.requirement("REQ-ASS-04")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_set_justification(self):
        """set_justification aggiorna correttamente la giustificazione."""
        asset = Asset.create("asset-1", "Asset 1", AssetType.SECURITY, "Desc",
                             answers=[Answer("req-1", justification="Vecchia")])
        asset.set_justification("req-1", "Nuova")
        assert asset.answers["req-1"].justification == "Nuova"

    @pytest.mark.requirement("REQ-ASS-04")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_set_justification_nonexistent_requirement_raises(self):
        """set_justification solleva RequirementNotFoundError se il requisito non esiste."""
        asset = Asset("asset-1", "Asset 1", AssetType.SECURITY, "Desc")
        with pytest.raises(RequirementNotFoundError):
            asset.set_justification("req-inesistente", "testo")

    # --- answers property ---

    @pytest.mark.requirement("REQ-ASS-05")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_answers_property_is_read_only(self):
        """La property answers restituisce un MappingProxyType immutabile."""
        asset = Asset("asset-1", "Asset 1", AssetType.SECURITY, "Desc")
        asset.add_answer(Answer("req-1"))
        with pytest.raises(TypeError):
            asset.answers["req-nuovo"] = Answer("req-nuovo")  # type: ignore


# ─────────────────────────────────────────────────────────────────────────────
# Device
# ─────────────────────────────────────────────────────────────────────────────

class TestDevice:

    # --- creazione ---

    @pytest.mark.requirement("REQ-DEV-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_init_minimal(self):
        """Device creato con __init__ ha _assets vuoto."""
        device = Device("d-1", "std-1", "Device 1", "Android", "Desc")
        assert device.id == "d-1"
        assert device.standard_id == "std-1"
        assert device.name == "Device 1"
        assert device.os == "Android"
        assert device.description == "Desc"
        assert len(device.assets) == 0

    @pytest.mark.requirement("REQ-DEV-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_create_with_assets(self):
        """Device.create inserisce gli asset iniziali tramite add_asset."""
        device = Device.create(
            device_id="d-1",
            standard_id="std-1",
            name="Device 1",
            os="Android",
            description="Desc",
            assets=[
                Asset("asset-1", "Asset 1", AssetType.SECURITY, "Desc"),
                Asset("asset-2", "Asset 2", AssetType.NETWORK, "Desc"),
            ],
        )
        assert len(device.assets) == 2
        assert "asset-1" in device.assets
        assert "asset-2" in device.assets

    @pytest.mark.requirement("REQ-DEV-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_create_with_none_assets(self):
        """Device.create con assets=None produce un Device senza asset."""
        device = Device.create("d-1", "std-1", "Device 1", "Android", "Desc", assets=None)
        assert len(device.assets) == 0

    @pytest.mark.requirement("REQ-DEV-01")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_create_with_duplicate_assets_raises(self):
        """Device.create con asset duplicati solleva DuplicateAssetError."""
        with pytest.raises(DuplicateAssetError):
            Device.create(
                device_id="d-1",
                standard_id="std-1",
                name="Device 1",
                os="Android",
                description="Desc",
                assets=[
                    Asset("asset-1", "Asset 1", AssetType.SECURITY, "Desc"),
                    Asset("asset-1", "Duplicato", AssetType.NETWORK, "Desc"),
                ],
            )

    # --- update_info ---

    @pytest.mark.requirement("REQ-DEV-02")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_update_info_all_fields(self):
        """update_info aggiorna tutti i campi anagrafici se forniti."""
        device = Device("d-1", "std-1", "Device 1", "Android", "Desc")
        device.update_info(name="Nuovo nome", os="iOS", description="Nuova desc")
        assert device.name == "Nuovo nome"
        assert device.os == "iOS"
        assert device.description == "Nuova desc"

    @pytest.mark.requirement("REQ-DEV-02")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_update_info_partial(self):
        """update_info con argomenti parziali aggiorna solo i campi forniti."""
        device = Device("d-1", "std-1", "Device 1", "Android", "Desc originale")
        device.update_info(name="Nuovo nome")
        assert device.name == "Nuovo nome"
        assert device.os == "Android"           # invariato
        assert device.description == "Desc originale"  # invariato

    # --- add_asset ---

    @pytest.mark.requirement("REQ-DEV-03")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_add_asset(self):
        """add_asset inserisce correttamente un nuovo Asset."""
        device = Device("d-1", "std-1", "Device 1", "Android", "Desc")
        device.add_asset(Asset("asset-1", "Asset 1", AssetType.SECURITY, "Desc"))
        assert "asset-1" in device.assets

    @pytest.mark.requirement("REQ-DEV-03")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_add_asset_duplicate_raises(self):
        """add_asset solleva DuplicateAssetError se l'id è già presente."""
        device = Device("d-1", "std-1", "Device 1", "Android", "Desc")
        device.add_asset(Asset("asset-1", "Asset 1", AssetType.SECURITY, "Desc"))
        with pytest.raises(DuplicateAssetError):
            device.add_asset(Asset("asset-1", "Duplicato", AssetType.NETWORK, "Desc"))

    @pytest.mark.requirement("REQ-DEV-03")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_add_asset_isolates_internal_state(self):
        """
        Modificare l'Asset originale dopo add_asset non deve alterare
        lo stato interno del Device (deepcopy, non shallow copy).
        """
        device = Device("d-1", "std-1", "Device 1", "Android", "Desc")
        asset = Asset.create("asset-1", "Asset 1", AssetType.SECURITY, "Desc",
                             answers=[Answer.create("req-1", node_choices={"node-1": True})])
        device.add_asset(asset)

        asset.set_node_choice("req-1", "node-1", False)

        assert device.assets["asset-1"].answers["req-1"].node_choices["node-1"] is True

    # --- remove_asset ---

    @pytest.mark.requirement("REQ-DEV-04")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_remove_asset(self):
        """remove_asset rimuove correttamente un Asset esistente."""
        device = Device("d-1", "std-1", "Device 1", "Android", "Desc")
        device.add_asset(Asset("asset-1", "Asset 1", AssetType.SECURITY, "Desc"))
        device.remove_asset("asset-1")
        assert "asset-1" not in device.assets

    @pytest.mark.requirement("REQ-DEV-04")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_remove_asset_nonexistent_raises(self):
        """remove_asset solleva AssetNotFoundError se l'asset non esiste."""
        device = Device("d-1", "std-1", "Device 1", "Android", "Desc")
        with pytest.raises(AssetNotFoundError):
            device.remove_asset("asset-inesistente")

    # --- update_asset ---

    @pytest.mark.requirement("REQ-DEV-05")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_update_asset_all_fields(self):
        """update_asset aggiorna tutti i campi dell'Asset se forniti."""
        device = Device("d-1", "std-1", "Device 1", "Android", "Desc")
        device.add_asset(Asset("asset-1", "Nome", AssetType.SECURITY, "Desc"))
        device.update_asset("asset-1", name="Nuovo", asset_type=AssetType.NETWORK, description="Nuova desc")
        updated = device.assets["asset-1"]
        assert updated.name == "Nuovo"
        assert updated.asset_type == AssetType.NETWORK
        assert updated.description == "Nuova desc"

    @pytest.mark.requirement("REQ-DEV-05")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_update_asset_partial(self):
        """update_asset con argomenti parziali aggiorna solo i campi forniti."""
        device = Device("d-1", "std-1", "Device 1", "Android", "Desc")
        device.add_asset(Asset("asset-1", "Nome originale", AssetType.SECURITY, "Desc originale"))
        device.update_asset("asset-1", name="Nome aggiornato")
        updated = device.assets["asset-1"]
        assert updated.name == "Nome aggiornato"
        assert updated.asset_type == AssetType.SECURITY    # invariato
        assert updated.description == "Desc originale"     # invariato

    @pytest.mark.requirement("REQ-DEV-05")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_update_asset_nonexistent_raises(self):
        """update_asset solleva AssetNotFoundError se l'asset non esiste."""
        device = Device("d-1", "std-1", "Device 1", "Android", "Desc")
        with pytest.raises(AssetNotFoundError):
            device.update_asset("asset-inesistente", name="X")

    # --- add_answer ---

    @pytest.mark.requirement("REQ-DEV-06")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_add_answer(self):
        """add_answer inserisce correttamente una Answer nell'Asset specificato."""
        device = Device("d-1", "std-1", "Device 1", "Android", "Desc")
        device.add_asset(Asset("asset-1", "Asset 1", AssetType.SECURITY, "Desc"))
        device.add_answer("asset-1", Answer.create("req-1", node_choices={"node-1": True}))
        assert "req-1" in device.assets["asset-1"].answers

    @pytest.mark.requirement("REQ-DEV-06")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_add_answer_nonexistent_asset_raises(self):
        """add_answer solleva AssetNotFoundError se l'asset non esiste."""
        device = Device("d-1", "std-1", "Device 1", "Android", "Desc")
        with pytest.raises(AssetNotFoundError):
            device.add_answer("asset-inesistente", Answer("req-1"))

    # --- set_node_choice ---

    @pytest.mark.requirement("REQ-DEV-07")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_set_node_choice(self):
        """set_node_choice aggiorna correttamente il valore nell'Asset specificato."""
        device = Device.create(
            device_id="d-1", standard_id="std-1", name="Device 1", os="Android", description="Desc",
            assets=[Asset.create("asset-1", "Asset 1", AssetType.SECURITY, "Desc",
                                 answers=[Answer.create("req-1", node_choices={"node-1": False})])],
        )
        device.set_node_choice("asset-1", "req-1", "node-1", True)
        assert device.assets["asset-1"].answers["req-1"].node_choices["node-1"] is True

    @pytest.mark.requirement("REQ-DEV-07")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_set_node_choice_does_not_affect_other_assets(self):
        """set_node_choice non deve alterare gli altri Asset nel Device."""
        device = Device.create(
            device_id="d-1", standard_id="std-1", name="Device 1", os="Android", description="Desc",
            assets=[
                Asset.create("asset-1", "Asset 1", AssetType.SECURITY, "Desc",
                             answers=[Answer.create("req-1", node_choices={"node-1": True})]),
                Asset.create("asset-2", "Asset 2", AssetType.NETWORK, "Desc",
                             answers=[Answer.create("req-1", node_choices={"node-1": True})]),
            ],
        )
        device.set_node_choice("asset-1", "req-1", "node-1", False)
        assert device.assets["asset-2"].answers["req-1"].node_choices["node-1"] is True

    @pytest.mark.requirement("REQ-DEV-07")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_set_node_choice_nonexistent_asset_raises(self):
        """set_node_choice solleva AssetNotFoundError se l'asset non esiste."""
        device = Device("d-1", "std-1", "Device 1", "Android", "Desc")
        with pytest.raises(AssetNotFoundError):
            device.set_node_choice("asset-inesistente", "req-1", "node-1", True)

    @pytest.mark.requirement("REQ-DEV-07")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_set_node_choice_nonexistent_requirement_raises(self):
        """set_node_choice solleva RequirementNotFoundError se il requisito non esiste."""
        device = Device("d-1", "std-1", "Device 1", "Android", "Desc")
        device.add_asset(Asset("asset-1", "Asset 1", AssetType.SECURITY, "Desc"))
        with pytest.raises(RequirementNotFoundError):
            device.set_node_choice("asset-1", "req-inesistente", "node-1", True)

    # --- set_justification ---

    @pytest.mark.requirement("REQ-DEV-08")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_set_justification(self):
        """set_justification aggiorna correttamente la giustificazione nell'Asset specificato."""
        device = Device.create(
            device_id="d-1", standard_id="std-1", name="Device 1", os="Android", description="Desc",
            assets=[Asset.create("asset-1", "Asset 1", AssetType.SECURITY, "Desc",
                                 answers=[Answer("req-1", justification="Vecchia")])],
        )
        device.set_justification("asset-1", "req-1", "Nuova")
        assert device.assets["asset-1"].answers["req-1"].justification == "Nuova"

    @pytest.mark.requirement("REQ-DEV-08")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_set_justification_does_not_affect_other_assets(self):
        """set_justification non deve alterare gli altri Asset nel Device."""
        device = Device.create(
            device_id="d-1", standard_id="std-1", name="Device 1", os="Android", description="Desc",
            assets=[
                Asset.create("asset-1", "Asset 1", AssetType.SECURITY, "Desc",
                             answers=[Answer("req-1", justification="Originale")]),
                Asset.create("asset-2", "Asset 2", AssetType.NETWORK, "Desc",
                             answers=[Answer("req-1", justification="Originale")]),
            ],
        )
        device.set_justification("asset-1", "req-1", "Aggiornata")
        assert device.assets["asset-2"].answers["req-1"].justification == "Originale"

    @pytest.mark.requirement("REQ-DEV-08")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_set_justification_nonexistent_asset_raises(self):
        """set_justification solleva AssetNotFoundError se l'asset non esiste."""
        device = Device("d-1", "std-1", "Device 1", "Android", "Desc")
        with pytest.raises(AssetNotFoundError):
            device.set_justification("asset-inesistente", "req-1", "testo")

    # --- assets property ---

    @pytest.mark.requirement("REQ-DEV-09")
    @pytest.mark.priority("high")
    @pytest.mark.type("unità")
    def test_assets_property_is_read_only(self):
        """La property assets restituisce un MappingProxyType immutabile."""
        device = Device("d-1", "std-1", "Device 1", "Android", "Desc")
        with pytest.raises(TypeError):
            device.assets["asset-nuovo"] = Asset("asset-nuovo", "X", AssetType.SECURITY, "Desc")  # type: ignore