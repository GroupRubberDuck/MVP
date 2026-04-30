from .asset import Asset,AssetSnapshot
from .answer import Answer
from .asset_type import AssetType
from .exceptions import DuplicateAssetError, AssetNotFoundError
# from ..shared.validators import is_blank,key_exists 
from dataclasses import dataclass
from types import MappingProxyType
import copy

@dataclass(frozen=True)
class DeviceSnapshot:
        id: str
        standard_id: str
        name: str
        os: str
        description: str
        assets: MappingProxyType[str, AssetSnapshot]

@dataclass(frozen=True)
class DeviceSummarySnapshot:
        id: str
        standard_id: str
        name: str
        os: str
        description: str
        assets:tuple[str, ...]



class Device:
    """Rappresenta un dispositivo da valutare, 
    con i suoi asset 
    e le risposte ai requirement."""
    def __init__(self, device_id: str,
                standard_id:str,
                name: str, 
                os: str, 
                description: str, 
                assets: list[Asset] | tuple[Asset, ...] | None = None):
        self._id = device_id
        self._standard_id = standard_id
        self._name = name
        self._os = os
        self._description = description
        self._assets: dict[str, Asset] = {}

        if assets is not None:
            for asset in assets:
                # Usiamo il metodo add_asset che ha GIA' il controllo dei duplicati!
                self.add_asset(asset)

                
    def _get_asset_by_id(self, asset_id: str) -> Asset:
        if asset_id not in self._assets:
            raise AssetNotFoundError(f"Asset con id '{asset_id}' non trovato nel dispositivo.")
        return self._assets[asset_id]


    @property
    def id(self) -> str:
        return self._id     
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def standard_id(self) -> str:
        return self._standard_id

    @property
    def os(self) -> str:
        return self._os
    
    @property
    def description(self) -> str:
        return self._description
    
    def set_name(self, name: str):
        self._name = name   
    
    def set_os(self, os: str):
        self._os = os
    
    def set_description(self, description: str):
        self._description = description 

    def add_asset(self, asset: Asset):
        if asset.id in self._assets:
            raise DuplicateAssetError(f"Asset con id '{asset.id}' già esistente nel dispositivo.")
        self._assets[asset.id] = copy.copy(asset)

    def remove_asset(self, asset_id: str):
        if asset_id not in self._assets:
            raise AssetNotFoundError(f"Asset con id '{asset_id}' non trovato nel dispositivo.")
        del self._assets[asset_id]

    def create_asset_snapshot(self, asset_id: str) -> AssetSnapshot:
        return self._get_asset_by_id(asset_id).create_snapshot()
    
    def create_summary_snapshot(self) -> DeviceSummarySnapshot:
        return DeviceSummarySnapshot(
            id=self._id,
            name=self._name,
            standard_id=self._standard_id,
            os=self._os,
            description=self._description,
            assets=tuple(self._assets.keys())
        )
    
    def create_snapshot(self) -> DeviceSnapshot:
        return DeviceSnapshot(
            id=self._id,
            name=self._name,
            standard_id=self._standard_id,
            os=self._os,
            description=self._description,
            assets=MappingProxyType({asset_id: asset.create_snapshot() for asset_id, asset in self._assets.items()})
        )
    

    def update_asset(self, asset_id: str, name: str | None = None, asset_type: AssetType | None = None, description: str | None = None):
        asset = self._get_asset_by_id(asset_id)
        if name is not None:
            asset.set_name(name)
        if asset_type is not None:
            asset.set_asset_type(asset_type)
        if description is not None:
            asset.set_description(description)

    def set_node_choice(self, asset_id: str,requirement_id:str, node_id: str, value: bool):
        asset = self._get_asset_by_id(asset_id)
        asset.set_node_choice(requirement_id, node_id, value)

    def set_justification(self, asset_id: str, requirement_id: str, justification: str):
        asset = self._get_asset_by_id(asset_id)
        asset.set_justification(requirement_id, justification)

    def add_answer(self, asset_id: str, answer: Answer):
        asset = self._get_asset_by_id(asset_id)
        asset.add_answer(answer)