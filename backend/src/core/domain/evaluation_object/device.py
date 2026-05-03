# device.py
from dataclasses import dataclass, field
from .asset import Asset
from .exceptions import DuplicateAssetError, AssetNotFoundError
# import copy
from types import MappingProxyType

@dataclass
class Device:
    id: str
    standard_id: str
    name: str
    os: str
    description: str
    _assets: dict[str, Asset] = field(default_factory=dict, repr=False)

    @classmethod
    def create(cls, device_id: str, standard_id: str, name: str,
               os: str, description: str,
               assets: list[Asset] | None = None) -> "Device":
        obj = cls(device_id, standard_id, name, os, description)
        for asset in (assets or []):
            obj.add_asset(asset)
        return obj

    # --- lettura ---
    @property
    def assets(self) -> MappingProxyType[str, Asset]:
        return MappingProxyType(self._assets)

    def get_asset(self, asset_id: str) -> Asset:
        if asset_id not in self._assets:
            raise AssetNotFoundError(
                f"Asset '{asset_id}' non trovato nel device '{self.id}'")
        return self._assets[asset_id]

    # --- scrittura anagrafica device ---
    def update_info(self, name: str | None = None,
                    os: str | None = None,
                    description: str | None = None) -> None:
        if name is not None: 
            self.name = name
        if os is not None: 
            self.os = os
        if description is not None: 
            self.description = description

    # --- gestione asset ---
    def add_asset(self, asset: Asset) -> None:
        if asset.id in self._assets:
            raise DuplicateAssetError(
                f"Asset '{asset.id}' già presente nel device '{self.id}'")
        self._assets[asset.id] = asset

    def remove_asset(self, asset_id: str) -> None:
        self.get_asset(asset_id)  # valida esistenza
        del self._assets[asset_id]



