from abc import abstractmethod
from typing import IO, Any
from types import MappingProxyType

from core.domain.evaluation_object.asset.asset import Asset
from core.domain.evaluation_object.asset.asset_anagraphic import AssetAnagraphic
from core.domain.evaluation_object.asset.asset_evidence import AssetEvidence
from core.domain.evaluation_object.asset.asset_proprieties import AssetProprieties
from core.domain.evaluation_object.asset.asset_type import AssetType
from core.domain.evaluation_object.device import Device

from core.ports.outbound.device.importer.file_device_importer_port import (
    FileDeviceImporterPort,
)

from core.ports.outbound.device.exceptions import (
    FileTooLargeError,
    MissingDeviceFieldError,
    InvalidAssetTypeError,
)

_REQUIRED_DEVICE_FIELDS = ("device_id", "standard_id", "name", "os", "description")
_MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


class FileDeviceImporter(FileDeviceImporterPort):
    def parse_device_file(self, device_file_content: IO[bytes]) -> Device:
        self._pre_validate(device_file_content)
        raw = self._deserialize(device_file_content)
        data = self._parse_data(raw)
        self._close_stream()
        return self._build_device(data)

    @abstractmethod
    def _deserialize(self, device_file_content: IO[bytes]) -> Any: ...

    @abstractmethod
    def _parse_data(self, raw: Any) -> dict: ...

    def _pre_validate(self, device_file_content: IO[bytes]) -> None:
        device_file_content.seek(0, 2)
        size = device_file_content.tell()
        device_file_content.seek(0)
        if size > _MAX_FILE_SIZE_BYTES:
            raise FileTooLargeError(
                "Il file supera la dimensione massima consentita di 10 MB."
            )

    def _close_stream(self) -> None:
        pass

    def _build_device(self, data: dict) -> Device:
        for field in _REQUIRED_DEVICE_FIELDS:
            if not data.get(field):
                raise MissingDeviceFieldError(
                    f"Campo obbligatorio mancante o vuoto: '{field}'."
                )
        assets = [self._build_asset(a) for a in data.get("assets", [])]
        return Device.create(
            device_id=data["device_id"],
            standard_id=data["standard_id"],
            name=data["name"],
            os=data["os"],
            description=data["description"],
            assets=assets,
        )

    def _build_asset(self, asset_data: dict) -> Asset:
        try:
            asset_type = AssetType(asset_data["asset_type"])
        except ValueError:
            raise InvalidAssetTypeError(
                f"Valore asset_type non valido: '{asset_data.get('asset_type')}'."
            )
        evidences = {
            ev["requirement_id"]: AssetEvidence(
                requirement_id=ev["requirement_id"],
                node_choices=MappingProxyType(ev.get("evaluation_map", {})),
                justification=ev.get("justification", ""),
            )
            for ev in asset_data.get("evaluations", [])
        }
        return Asset(
            id=asset_data["id"],
            anagraphic=AssetAnagraphic(
                name=asset_data["name"],
                asset_type=asset_type,
                description=asset_data["description"],
            ),
            proprieties=AssetProprieties(evidences=evidences),
        )
