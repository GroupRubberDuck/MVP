import io
import json
import pytest

from adapters.outbound.device.importer.json_file_device_importer import JSONFileDeviceImporter
from core.ports.outbound.device.exceptions import InvalidFileFormatError


def _to_stream(data: dict) -> io.BytesIO:
    return io.BytesIO(json.dumps(data).encode())


def _base_data(**overrides) -> dict:
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


@pytest.fixture
def importer() -> JSONFileDeviceImporter:
    return JSONFileDeviceImporter()


class TestJSONFileDeviceImporter:

    def test_parses_valid_json(self, importer):
        device = importer.parse_device_file(_to_stream(_base_data()))
        assert device.id == "DEV-001"
        assert device.standard_id == "STD-001"

    def test_standard_id_read_from_file(self, importer):
        device = importer.parse_device_file(_to_stream(_base_data(standard_id="XYZ")))
        assert device.standard_id == "XYZ"

    def test_parses_device_with_assets(self, importer):
        asset = {"id": "A1", "name": "WiFi", "asset_type": "network",
                 "description": "d", "evaluations": []}
        device = importer.parse_device_file(_to_stream(_base_data(assets=[asset])))
        assert "A1" in device.assets

    def test_parses_device_with_evaluations(self, importer):
        evaluation = {"requirement_id": "REQ-1",
                      "evaluation_map": {"N1": True}, "justification": "ok"}
        asset = {"id": "A1", "name": "WiFi", "asset_type": "network",
                 "description": "d", "evaluations": [evaluation]}
        device = importer.parse_device_file(_to_stream(_base_data(assets=[asset])))
        assert device.assets["A1"].get_evidence("REQ-1").node_choices["N1"] is True

    def test_raises_invalid_format_on_malformed_json(self, importer):
        with pytest.raises(InvalidFileFormatError):
            importer.parse_device_file(io.BytesIO(b"{not valid json"))