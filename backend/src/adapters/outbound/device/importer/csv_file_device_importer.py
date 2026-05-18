import csv
import io
from typing import IO

from adapters.outbound.device.importer.file_device_importer import FileDeviceImporter
from core.ports.outbound.device.exceptions import InvalidFileFormatError


class CSVFileDeviceImporter(FileDeviceImporter):
    def _deserialize(self, device_file_content: IO[bytes]) -> list[dict]:
        try:
            text = io.TextIOWrapper(device_file_content, encoding="utf-8")
            return list(csv.DictReader(text))
        except (UnicodeDecodeError, csv.Error) as e:
            raise InvalidFileFormatError(f"File CSV non leggibile: {e}") from e

    def _parse_data(self, raw: list[dict]) -> dict:
        if not raw:
            from core.ports.outbound.device.exceptions import EmptyFileError

            raise EmptyFileError("Il file CSV non contiene righe.")

        first = raw[0]
        assets_by_id: dict[str, dict] = {}
        evaluations_by_asset_req: dict[tuple[str, str], dict] = {}

        for row in raw:
            asset_id = row.get("asset_id")
            if not asset_id:
                continue

            if asset_id not in assets_by_id:
                assets_by_id[asset_id] = {
                    "id": asset_id,
                    "name": row.get("asset_name", ""),
                    "asset_type": row.get("asset_type", ""),
                    "description": row.get("asset_description", ""),
                    "evaluations": [],
                }

            req_id = row.get("requirement_id")
            node_id = row.get("node_id")

            if not req_id:
                continue

            ev_key = (asset_id, req_id)
            if ev_key not in evaluations_by_asset_req:
                ev = {
                    "requirement_id": req_id,
                    "evaluation_map": {},
                    "justification": row.get("justification", ""),
                }
                evaluations_by_asset_req[ev_key] = ev
                assets_by_id[asset_id]["evaluations"].append(ev)
            else:
                ev = evaluations_by_asset_req[ev_key]

            if node_id:
                ev["evaluation_map"][node_id] = (
                    row.get("node_value", "").lower() == "true"
                )

        return {
            "device_id": first.get("device_id", ""),
            "standard_id": first.get("standard_id", ""),
            "name": first.get("name", ""),
            "os": first.get("os", ""),
            "description": first.get("description", ""),
            "assets": list(assets_by_id.values()),
        }
