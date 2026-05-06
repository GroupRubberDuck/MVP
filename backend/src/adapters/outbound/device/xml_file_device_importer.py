import xml.etree.ElementTree as ET
from typing import IO

from adapters.outbound.device.file_device_importer import FileDeviceImporter
from core.ports.outbound.device.exceptions import InvalidFileFormatError


class XMLFileDeviceImporter(FileDeviceImporter):

    def _deserialize(self, device_file_content: IO[bytes]) -> ET.Element:
        try:
            return ET.parse(device_file_content).getroot()
        except ET.ParseError as e:
            raise InvalidFileFormatError(f"File XML malformato: {e}") from e

    def _parse_data(self, raw: ET.Element) -> dict:
        assets = []
        for asset_el in raw.findall("assets/asset"):
            evaluations = []
            for ev_el in asset_el.findall("evaluations/evaluation"):
                evaluation_map = {
                    entry.get("node_id"): (entry.text or "").strip().lower() == "true"
                    for entry in ev_el.findall("evaluation_map/entry")
                }
                evaluations.append({
                    "requirement_id": ev_el.findtext("requirement_id", ""),
                    "evaluation_map": evaluation_map,
                    "justification": ev_el.findtext("justification", ""),
                })
            assets.append({
                "id": asset_el.findtext("id", ""),
                "name": asset_el.findtext("name", ""),
                "asset_type": asset_el.findtext("asset_type", ""),
                "description": asset_el.findtext("description", ""),
                "evaluations": evaluations,
            })
        return {
            "device_id": raw.findtext("device_id", ""),
            "standard_id": raw.findtext("standard_id", ""),
            "name": raw.findtext("name", ""),
            "os": raw.findtext("os", ""),
            "description": raw.findtext("description", ""),
            "assets": assets,
        }