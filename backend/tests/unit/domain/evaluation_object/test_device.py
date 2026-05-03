import pytest
from core.domain.evaluation_object.asset import Asset
from core.domain.evaluation_object.asset_type import AssetType
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
    asset = Asset.create(
        asset_id="A1", name="Test Asset",
        asset_type=AssetType.NETWORK, description="Test",
    )
    return Device.create(
        device_id="DEV-1", standard_id="EN-18031",
        name="Smart Router", os="Linux", description="Router di test",
        assets=[asset],
    )


def _make_asset(asset_id="ASSET-1"):
    return Asset.create(
        asset_id=asset_id, name="Test Asset",
        asset_type=AssetType.NETWORK, description="Test",
    )


# ── Creazione ──

class TestDeviceCreation:

    def test_create_empty(self, device_vuoto):
        assert device_vuoto.id == "DEV-1"
        assert device_vuoto.standard_id == "EN-18031"
        assert len(device_vuoto.assets) == 0

    def test_create_with_assets(self):
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
        device_vuoto.add_asset(_make_asset("A1"))
        assert "A1" in device_vuoto.assets

    def test_add_duplicate_raises(self, device_con_asset):
        with pytest.raises(DuplicateAssetError):
            device_con_asset.add_asset(_make_asset("A1"))

    def test_remove_asset(self, device_con_asset):
        device_con_asset.remove_asset("A1")
        assert "A1" not in device_con_asset.assets

    def test_remove_nonexistent_raises(self, device_vuoto):
        with pytest.raises(AssetNotFoundError):
            device_vuoto.remove_asset("A999")

    def test_get_asset(self, device_con_asset):
        assert device_con_asset.get_asset("A1").id == "A1"

    def test_get_nonexistent_raises(self, device_vuoto):
        with pytest.raises(AssetNotFoundError):
            device_vuoto.get_asset("A999")

    def test_assets_immutable_view(self, device_vuoto):
        with pytest.raises(TypeError):
            device_vuoto.assets["A1"] = _make_asset("A1")

    def test_add_asset_stores_same_reference(self, device_vuoto):
        original = _make_asset("A1")
        device_vuoto.add_asset(original)
        assert device_vuoto.get_asset("A1") is original


# ── update_info ──

class TestDeviceUpdateInfo:

    def test_update_name(self, device_vuoto):
        device_vuoto.update_info(name="Nuovo")
        assert device_vuoto.name == "Nuovo"

    def test_update_os(self, device_vuoto):
        device_vuoto.update_info(os="Windows")
        assert device_vuoto.os == "Windows"

    def test_update_partial_preserves(self, device_vuoto):
        device_vuoto.update_info(name="Nuovo")
        assert device_vuoto.os == "Linux"
        assert device_vuoto.description == "Router di test"

    def test_update_none_noop(self, device_vuoto):
        device_vuoto.update_info()
        assert device_vuoto.name == "Smart Router"


