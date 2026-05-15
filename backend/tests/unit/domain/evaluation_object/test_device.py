import pytest
from core.domain.evaluation_object.asset import Asset,AssetAnagraphic
from core.domain.evaluation_object.asset.asset_type import AssetType
from core.domain.evaluation_object.device import Device
from core.domain.evaluation_object.exceptions import DuplicateAssetError, AssetNotFoundError


# ── Fixtures ──

@pytest.fixture
def device_vuoto():
    return Device.create(
        device_id="DEV-1", standard_id="EN-18031",
        name="Smart Router", os="Linux", description="Router di test",
    )


@pytest.fixture
def device_con_asset():
    asset = Asset(
        id="A1", 
        anagraphic=AssetAnagraphic (name="Test Asset", asset_type=AssetType.NETWORK, description="Test"),
    )
    return Device.create(
        device_id="DEV-1", standard_id="EN-18031",
        name="Smart Router", os="Linux", description="Router di test",
        assets=[asset],
    )


def _make_asset(asset_id="ASSET-1"):
    return Asset(
        id=asset_id, anagraphic=AssetAnagraphic(name="Test Asset", asset_type=AssetType.NETWORK, description="Test")
    )


# ── Creazione ──

class TestDeviceCreation:

    def test_create_empty(self, device_vuoto):
        """
        Dati i parametri identificativi e anagrafici corretti (Given),
        quando viene creato un nuovo Device tramite il metodo factory (When),
        allora l'entità deve essere istanziata correttamente con una lista di asset vuota (Then).
        """
        assert device_vuoto.id == "DEV-1"
        assert device_vuoto.standard_id == "EN-18031"
        assert len(device_vuoto.assets) == 0

    def test_create_with_assets(self):
        """
        Dato un elenco predefinito di asset (Given),
        quando un Device viene creato includendo tale elenco (When),
        allora l'entità deve contenere tutti gli asset forniti all'interno del suo dizionario interno (Then).
        """
        device = Device.create(
            device_id="DEV-1", standard_id="EN-18031",
            name="Router", os="Linux", description="Test",
            assets=[_make_asset("A1"), _make_asset("A2")],
        )
        assert len(device.assets) == 2
        assert "A1" in device.assets
        assert "A2" in device.assets


# ── Gestione Asset ──

class TestDeviceAssetManagement:

    def test_add_asset(self, device_vuoto):
        """
        Dato un Device vuoto e un nuovo Asset (Given),
        quando l'asset viene aggiunto al dispositivo (When),
        allora deve essere rintracciabile tramite il suo identificatore univoco (Then).
        """
        device_vuoto.add_asset(_make_asset("A1"))
        assert "A1" in device_vuoto.assets

    def test_add_duplicate_raises(self, device_con_asset):
        """
        Dato un Device che contiene già un asset con un determinato ID (Given),
        quando si tenta di aggiungere un altro asset con lo stesso ID (When),
        allora il sistema deve impedire l'operazione sollevando un DuplicateAssetError (Then).
        """
        with pytest.raises(DuplicateAssetError):
            device_con_asset.add_asset(_make_asset("A1"))

    def test_remove_asset(self, device_con_asset):
        """
        Dato un Device contenente un asset (Given),
        quando l'asset viene rimosso specificando il suo ID (When),
        allora non deve più risultare presente nella collezione del dispositivo (Then).
        """
        device_con_asset.remove_asset("A1")
        assert "A1" not in device_con_asset.assets

    def test_remove_nonexistent_raises(self, device_vuoto):
        """
        Dato un Device (Given),
        quando si tenta di rimuovere un ID asset non presente (When),
        allora l'operazione deve fallire sollevando un AssetNotFoundError (Then).
        """
        with pytest.raises(AssetNotFoundError):
            device_vuoto.remove_asset("A999")

    def test_get_asset(self, device_con_asset):
        """
        Dato un Device popolato (Given),
        quando viene richiesto un asset tramite il suo ID (When),
        allora deve restituire l'istanza corretta dell'entità Asset corrispondente (Then).
        """
        assert device_con_asset.get_asset("A1").id == "A1"

    def test_get_nonexistent_raises(self, device_vuoto):
        """
        Dato un Device (Given),
        quando si richiede un asset con un ID inesistente (When),
        allora deve essere sollevata un'eccezione AssetNotFoundError (Then).
        """
        with pytest.raises(AssetNotFoundError):
            device_vuoto.get_asset("A999")

    def test_assets_immutable_view(self, device_vuoto):
        """
        Dato un Device (Given),
        quando si tenta di manipolare direttamente il dizionario restituito dalla proprietà assets (When),
        allora deve essere sollevato un errore poiché la vista esposta deve essere immutabile per proteggere l'incapsulamento (Then).
        """
        with pytest.raises(TypeError):
            device_vuoto.assets["A1"] = _make_asset("A1")

    def test_add_asset_stores_same_reference(self, device_vuoto):
        """
        Dato un Device e un'istanza specifica di un Asset (Given),
        quando l'asset viene aggiunto (When),
        allora il dispositivo deve memorizzare esattamente lo stesso riferimento all'oggetto ricevuto (Then).
        """
        original = _make_asset("A1")
        device_vuoto.add_asset(original)
        assert device_vuoto.get_asset("A1") is original


# ── update_info ──

class TestDeviceUpdateInfo:

    def test_update_name(self, device_vuoto):
        """
        Dato un Device esistente (Given),
        quando viene aggiornato il nome (When),
        allora la proprietà name del dispositivo deve riflettere immediatamente il nuovo valore (Then).
        """
        device_vuoto.update_info(name="Nuovo")
        assert device_vuoto.name == "Nuovo"

    def test_update_os(self, device_vuoto):
        """
        Dato un Device (Given),
        quando viene modificata l'informazione sul sistema operativo (When),
        allora il campo os deve risultare correttamente aggiornato (Then).
        """
        device_vuoto.update_info(os="Windows")
        assert device_vuoto.os == "Windows"

    def test_update_partial_preserves(self, device_vuoto):
        """
        Dato un Device con informazioni complete (Given),
        quando viene aggiornato solo uno dei campi (es. il nome) (When),
        allora gli altri attributi anagrafici devono mantenere i loro valori originali (Then).
        """
        device_vuoto.update_info(name="Nuovo")
        assert device_vuoto.os == "Linux"
        assert device_vuoto.description == "Router di test"

    def test_update_none_noop(self, device_vuoto):
        """
        Dato un Device (Given),
        quando il metodo di aggiornamento viene invocato senza argomenti (When),
        allora lo stato dell'entità deve rimanere completamente invariato (Then).
        """
        device_vuoto.update_info()
        assert device_vuoto.name == "Smart Router"


