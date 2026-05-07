import csv
import io
from typing import IO

from adapters.outbound.device.file_device_importer import FileDeviceImporter
from core.ports.outbound.device.exceptions import InvalidFileFormatError, EmptyFileError


class CSVFileDeviceImporter(FileDeviceImporter):

    def _deserialize(self, device_file_content: IO[bytes]) -> list[dict]:
        try:
            text = io.TextIOWrapper(device_file_content, encoding="utf-8")
            return list(csv.DictReader(text))
        except (UnicodeDecodeError, csv.Error) as e:
            raise InvalidFileFormatError(f"File CSV non leggibile: {e}") from e

    def _parse_data(self, raw: list[dict]) -> dict:
        if not raw:
            raise EmptyFileError("Il file CSV non contiene righe.")
        first = raw[0]
        assets_by_id: dict[str, dict] = {}
        for row in raw:
            asset_id = row["asset_id"]
            if asset_id not in assets_by_id:
                assets_by_id[asset_id] = {
                    "id": asset_id,
                    "name": row["asset_name"],
                    "asset_type": row["asset_type"],
                    "description": row["asset_description"],
                    "evaluations": [],
                }
        return {
            "device_id": first["device_id"],
            "standard_id": first["standard_id"],
            "name": first["name"],
            "os": first["os"],
            "description": first["description"],
            "assets": list(assets_by_id.values()),
        }