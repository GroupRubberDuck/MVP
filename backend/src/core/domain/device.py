from pydantic import BaseModel, Enum

class AssetType(str, Enum):
    SECURITY = 'security'
    NETWORK = 'network'

class Asset(BaseModel):
    id: str
    name: str
    type: AssetType
    description: str

class Device(BaseModel):
    id: str
    name: str
    os: str
    description: str
    assets: list[Asset]

    def add_asset(self, asset: Asset) -> None:
        self.assets.append(asset)

    def remove_asset(self, asset: Asset) -> None:
        self.assets.remove(asset)



