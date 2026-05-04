from dataclasses import dataclass, field

from .asset_anagraphic import AssetAnagraphic
from .asset_proprieties import AssetProprieties
from .asset_evidence import AssetEvidence
from .asset_type import AssetType


@dataclass(frozen=True)
class Asset:
    id: str
    anagraphic: AssetAnagraphic
    proprieties: AssetProprieties = field(default_factory=AssetProprieties)

    def set_node_choice(self, requirement_id: str,
                        node_id: str, value: bool) -> None:
        self.proprieties.set_node_choice(requirement_id, node_id, value)

    def set_justification(self, requirement_id: str,
                          justification: str) -> None:
        self.proprieties.set_justification(requirement_id, justification)

    def update_anagraphic(self, name: str | None = None,
                          asset_type: AssetType | None = None,
                          description: str | None = None) -> "Asset":
        new_anagraphic = AssetAnagraphic(
            name=name if name is not None else self.anagraphic.name,
            asset_type=asset_type if asset_type is not None else self.anagraphic.asset_type,
            description=description if description is not None else self.anagraphic.description,
        )
        return Asset(
            id=self.id,
            anagraphic=new_anagraphic,
            proprieties=self.proprieties,
        )
    
    def get_evidence(self, requirement_id: str) -> AssetEvidence|None:
        return self.proprieties.get_evidence(requirement_id)