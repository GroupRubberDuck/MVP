import json
from src.core.services.device.device_file_command import DeviceFileCommand
from .file_device_exporter import FileDeviceExporter


class JSONFileDeviceExporter(FileDeviceExporter):

    def __init__(self):
        self._data: dict = {}

    def _prepare_structure(self, device_dto: DeviceFileCommand) -> None:
        # Inizializza il dizionario root con l'id del device
        self._data = {"id": device_dto.device.id}

    def _write_data(self, device_dto: DeviceFileCommand) -> None:
        device = device_dto.device

        # Anagrafica device
        self._data["standard_id"] = device.standard_id
        self._data["name"] = device.name
        self._data["os"] = device.os
        self._data["description"] = device.description

        # Assets
        self._data["assets"] = []
        for asset in device.assets.values():
            asset_data = {
                "id": asset.id,
                "anagraphic": {
                    "name": asset.anagraphic.name,
                    "asset_type": asset.anagraphic.asset_type.value,
                    "description": asset.anagraphic.description,
                },
                "evidences": [
                    {
                        "requirement_id": evidence.requirement_id,
                        "node_choices": {
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