import json
from typing import IO

from adapters.outbound.device.file_device_importer import FileDeviceImporter
from core.ports.outbound.device.exceptions import InvalidFileFormatError


class JSONFileDeviceImporter(FileDeviceImporter):

    def _check_metadata(self, device_file_content: IO[bytes]) -> None:
        pass

    def _open_stream(self, device_file_content: IO[bytes]) -> dict:
        try:
            return json.load(device_file_content)
        except json.JSONDecodeError as e:
            raise InvalidFileFormatError(f"File JSON malformato: {e}") from e

    def _parse_data(self, raw: dict) -> dict:
        return raw