from types import MappingProxyType
from pymongo.collection import Collection

from core.domain.evaluation_object.asset.asset import Asset
from core.domain.evaluation_object.asset.asset_anagraphic import AssetAnagraphic
from core.domain.evaluation_object.asset.asset_evidence import AssetEvidence
from core.domain.evaluation_object.asset.asset_proprieties import AssetProprieties
from core.domain.evaluation_object.asset.asset_type import AssetType
from core.domain.evaluation_object.device import Device

from core.ports.outbound.device.delete_device_port import DeleteDevicePort
from core.ports.outbound.device.find_all_device_port import FindAllDevicePort, DeviceSummary
from core.ports.outbound.device.find_device_port import FindDevicePort
from core.ports.outbound.device.register_device_port import RegisterDevicePort
from core.ports.outbound.device.save_device_port import SaveDevicePort


class MongoDeviceAdapter(
    SaveDevicePort, RegisterDevicePort, DeleteDevicePort,
    FindDevicePort, FindAllDevicePort,
):
    def __init__(self, collection: Collection) -> None:
        self._collection = collection

    def register(self, device: Device) -> None:
        doc = self._to_document(device)
        doc["_id"] = device.id
        self._collection.insert_one(doc)

    def save(self, device: Device) -> None:
        doc = self._to_document(device)
        self._collection.replace_one({"_id": device.id}, doc)

    def delete(self, device_id: str) -> None:
        self._collection.delete_one({"_id": device_id})

    def find_by_id(self, device_id: str) -> Device:
        doc = self._collection.find_one({"_id": device_id})
        if doc is None:
            raise KeyError(f"Device '{device_id}' non trovato.")
        return self._from_document(doc)

    def find_all(self) -> list[DeviceSummary]:
        return [
            DeviceSummary(
                device_id=str(doc["_id"]),
                name=doc["name"],
                os=doc["os"],
                description=doc["description"],
                compliance_standard_id=doc["compliance_standard_id"],
            )
            for doc in self._collection.find({}, {"assets": 0})
        ]

    def _to_document(self, device: Device) -> dict:
        return {
            "name": device.name,
            "os": device.os,
            "description": device.description,
            "compliance_standard_id": device.standard_id,
            "assets": [
                {
                    "id": asset.id,
                    "name": asset.anagraphic.name,
                    "type": asset.anagraphic.asset_type.value,
                    "description": asset.anagraphic.description,
                    "evaluations": [
                        {
                            "id": evidence.requirement_id,
                            "evaluation_map": dict(evidence.node_choices),
                            "justification": evidence.justification,
                        }
                        for evidence in asset.proprieties.evidences.values()
                    ],
                }
                for asset in device.assets.values()
            ],
        }

    def _from_document(self, doc: dict) -> Device:
        assets = []
        for asset_doc in doc.get("assets", []):
            evidences = {
                ev["id"]: AssetEvidence(
                    requirement_id=ev["id"],
                    node_choices=MappingProxyType(ev.get("evaluation_map", {})),
                    justification=ev.get("justification", ""),
                )
                for ev in asset_doc.get("evaluations", [])
            }
            assets.append(Asset(
                id=asset_doc["id"],
                anagraphic=AssetAnagraphic(
                    name=asset_doc["name"],
                    asset_type=AssetType(asset_doc["type"]),
                    description=asset_doc["description"],
                ),
                proprieties=AssetProprieties(evidences=evidences),
            ))
        return Device.create(
            device_id=str(doc["_id"]),
            standard_id=doc["compliance_standard_id"],
            name=doc["name"],
            os=doc["os"],
            description=doc["description"],
            assets=assets,
        )