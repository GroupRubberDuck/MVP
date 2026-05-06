import io
import pytest
from unittest.mock import MagicMock

from adapters.inbound.utilities.upload_file_controller import UploadFileController
from core.ports.inbound.device.import_device_use_case import AllowedDeviceFileExtension


class TestGetHttpFileExtension:

    def test_returns_csv_extension(self):
        result = UploadFileController.get_http_file_extension("device.csv")
        assert result == AllowedDeviceFileExtension.CSV

    def test_returns_json_extension(self):
        result = UploadFileController.get_http_file_extension("device.json")
        assert result == AllowedDeviceFileExtension.JSON

    def test_returns_xml_extension(self):
        result = UploadFileController.get_http_file_extension("device.xml")
        assert result == AllowedDeviceFileExtension.XML

    def test_extension_is_case_insensitive(self):
        result = UploadFileController.get_http_file_extension("device.CSV")
        assert result == AllowedDeviceFileExtension.CSV

    def test_raises_when_no_extension(self):
        with pytest.raises(ValueError, match="non ha un'estensione"):
            UploadFileController.get_http_file_extension("device")

    def test_raises_when_unsupported_extension(self):
        with pytest.raises(ValueError, match="non supportata"):
            UploadFileController.get_http_file_extension("device.txt")

    def test_uses_last_dot_segment(self):
        result = UploadFileController.get_http_file_extension("my.device.json")
        assert result == AllowedDeviceFileExtension.JSON


class TestGetHttpFilePayload:

    def test_returns_file_storage_stream(self):
        stream = io.BytesIO(b"contenuto")
        file_storage = MagicMock()
        file_storage.stream = stream

        result = UploadFileController.get_http_file_payload(file_storage)

        assert result is stream