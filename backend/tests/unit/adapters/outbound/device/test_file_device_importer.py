import io
import pytest

from adapters.outbound.device.file_device_importer import FileDeviceImporter
from core.domain.evaluation_object.asset.asset_type import AssetType
from core.ports.outbound.device.exceptions import (
    InvalidAssetTypeError,
    MissingDeviceFieldError,
)


class _StubImporter(FileDeviceImporter):
    def __init__(self, data: dict):
        self._data = data

    def _check_metadata(self, content) -> None:
        pass

    def _open_stream(self, content) -> dict:
        return self._data

    def _parse_data(self, raw) -> dict:
        return raw


def _full_data(**overrides) -> dict:
    base = {
        "device_id": "DEV-001",
        "standard_id": "STD-001",
        "name": "Router",
        "os": "Linux",
        "description": "Test",
        "assets": [],
    }
    base.update(overrides)
    return base


def _asset_data(**overrides) -> dict:
    base = {
        "id": "ASSET-001",
        "name": "WiFi",
        "asset_type": "network",
        "description": "desc",
        "evaluations": [],
    }
    base.update(overrides)
    return base


class TestBuildDevice:

    def test_builds_device_with_correct_fields(self):
        device = _StubImporter(_full_data()).parse_device_file(io.BytesIO())
        assert device.id == "DEV-001"
        assert device.standard_id == "STD-001"
        assert device.name == "Router"
        assert device.os == "Linux"

    def test_builds_device_without_assets(self):
        device = _StubImporter(_full_data()).parse_device_file(io.BytesIO())
        assert len(device.assets) == 0

    def test_builds_device_with_assets(self):
        data = _full_data(assets=[_asset_data(id="A1"), _asset_data(id="A2")])
        device = _StubImporter(data).parse_device_file(io.BytesIO())
        assert len(device.assets) == 2
        assert "A1" in device.assets

    def test_raises_missing_field_when_device_id_empty(self):
        with pytest.raises(MissingDeviceFieldError):
            _StubImporter(_full_data(device_id="")).parse_device_file(io.BytesIO())

    def test_raises_missing_field_when_standard_id_empty(self):
        with pytest.raises(MissingDeviceFieldError):
            _StubImporter(_full_data(standard_id="")).parse_device_file(io.BytesIO())

    def test_raises_missing_field_when_name_empty(self):
        with pytest.raises(MissingDeviceFieldError):
            _StubImporter(_full_data(name="")).parse_device_file(io.BytesIO())


class TestBuildAsset:

    def test_builds_asset_with_correct_type(self):
        data = _full_data(assets=[_asset_data(asset_type="security")])
        device = _StubImporter(data).parse_device_file(io.BytesIO())
        assert device.assets["ASSET-001"].anagraphic.asset_type == AssetType.SECURITY

    def test_builds_asset_with_evidence(self):
        evaluation = {
            "requirement_id": "REQ-1",
            "evaluation_map": {"N1": True},
            "justification": "ok",
        }
        data = _full_data(assets=[_asset_data(evaluations=[evaluation])])
        device = _StubImporter(data).parse_device_file(io.BytesIO())
        evidence = device.assets["ASSET-001"].get_evidence("REQ-1")
        assert evidence is not None
        assert evidence.node_choices["N1"] is True
        assert evidence.justification == "ok"

    def test_builds_asset_without_evaluations(self):
        data = _full_data(assets=[_asset_data(evaluations=[])])
        device = _StubImporter(data).parse_device_file(io.BytesIO())
        assert device.assets["ASSET-001"].get_evidence("REQ-1") is None

    def test_raises_invalid_asset_type_on_unknown_value(self):
        data = _full_data(assets=[_asset_data(asset_type="unknown")])
        with pytest.raises(InvalidAssetTypeError):
            _StubImporter(data).parse_device_file(io.BytesIO())