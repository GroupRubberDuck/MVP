import json
from .file_device_exporter import FileDeviceExporter
from core.domain.evaluation_object.device import Device

class JSONFileDeviceExporter(FileDeviceExporter):

    def __init__(self) -> None:
        self._data: dict = {}

    def _prepare_structure(self, device: Device) -> None:
        self._data = {"device_id": device.id}

    def _write_data(self, device: Device) -> None:
        self._data["standard_id"] = device.standard_id
        self._data["name"] = device.name
        self._data["os"] = device.os
        self._data["description"] = device.description

        self._data["assets"] = []
        for asset in device.assets.values():
            asset_data = {
                "id": asset.id,
                "name": asset.anagraphic.name,
                "asset_type": asset.anagraphic.asset_type.value,
                "description": asset.anagraphic.description,
                
                "evaluations": [
                    {
                        "requirement_id": evidence.requirement_id,
                        "evaluation_map": {
                            node_id: value
                            for node_id, value in evidence.node_choices.items()
                        },
                        "justification": evidence.justification,
                    }
                    for evidence in asset.proprieties.evidences.values()
                ],
            }
            self._data["assets"].append(asset_data)

    def _finalize_output(self) -> bytes:
        return json.dumps(self._data, ensure_ascii=False, indent=2).encode("utf-8")