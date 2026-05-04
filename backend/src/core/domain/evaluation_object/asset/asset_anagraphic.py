from dataclasses import dataclass

from .asset_type import AssetType


@dataclass(frozen=True)
class AssetAnagraphic:
    name: str
    asset_type: AssetType
    description: str