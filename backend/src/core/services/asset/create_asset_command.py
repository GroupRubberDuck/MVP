from dataclasses import dataclass
from ...domain.evaluation_object.asset.asset_type import AssetType

@dataclass
class CreateAssetCommand:
    name: str
    asset_type: AssetType
    description: str
    session_id: str