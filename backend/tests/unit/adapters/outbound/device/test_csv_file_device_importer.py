import io
import pytest

from adapters.outbound.device.importer.csv_file_device_importer import CSVFileDeviceImporter
from core.ports.outbound.device.exceptions import EmptyFileError, InvalidFileFormatError


_HEADER = "device_id,standard_id,name,os,description,asset_id,asset_name,asset_type,asset_description\n"


def _to_stream(*rows: str) -> io.BytesIO:
    content = _HEADER + "".join(rows)
    return io.BytesIO(content.encode())


def _row(device_id="DEV-001", standard_id="STD-001", name="Router",
         os="Linux", description="Test", asset_id="A1",
         asset_name="WiFi", asset_type="network", asset_description="desc") -> str:
    return f"{device_id},{standard_id},{name},{os},{description},{asset_id},{asset_name},{asset_type},{asset_description}\n"


@pytest.fixture
def importer() -> CSVFileDeviceImporter:
    return CSVFileDeviceImporter()


class TestCSVFileDeviceImporter:

    def test_parses_single_row(self, importer):
        device = importer.parse_device_file(_to_stream(_row()))
        assert device.id == "DEV-001"
        assert device.standard_id == "STD-001"

    def test_single_asset(self, importer):
        device = importer.parse_device_file(_to_stream(_row(asset_id="A1")))
        assert "A1" in device.assets

    def test_groups_multiple_rows_into_one_device(self, importer):
        device = importer.parse_device_file(
            _to_stream(_row(asset_id="A1"), _row(asset_id="A2"))
        )
        assert len(device.assets) == 2

    def test_deduplicates_same_asset_id(self, importer):
        device = importer.parse_device_file(
            _to_stream(_row(asset_id="A1"), _row(asset_id="A1"))
        )
        assert len(device.assets) == 1

    def test_raises_empty_file_on_no_rows(self, importer):
        stream = io.BytesIO(_HEADER.encode())
        with pytest.raises(EmptyFileError):
            importer.parse_device_file(stream)

    def test_raises_invalid_format_on_encoding_error(self, importer):
        stream = io.BytesIO(b"\xff\xfe\x00 contenuto non utf-8")
        with pytest.raises(InvalidFileFormatError):
            importer.parse_device_file(stream)