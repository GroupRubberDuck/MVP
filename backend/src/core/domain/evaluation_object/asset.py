# asset.py
from dataclasses import dataclass, field
from types import MappingProxyType

from .asset_type import AssetType


@dataclass(frozen=True)
class AssetAnagraphic:
    name: str
    asset_type: AssetType
    description: str


@dataclass(frozen=True)
class AssetEvidence:
    requirement_id: str
    node_choices: MappingProxyType[str, bool] = field(
        default_factory=lambda: MappingProxyType({})
    )
    justification: str = ""

    def with_node_choice(self, node_id: str, value: bool) -> "AssetEvidence":
        new_choices = dict(self.node_choices)
        new_choices[node_id] = value
        return AssetEvidence(
            requirement_id=self.requirement_id,
            node_choices=MappingProxyType(new_choices),
            justification=self.justification,
        )

    def with_justification(self, justification: str) -> "AssetEvidence":
        return AssetEvidence(
            requirement_id=self.requirement_id,
            node_choices=self.node_choices,
            justification=justification,
        )


class AssetProprieties:
    """
    Classe che gestisce le AssetEvidence
    indicizzate per requirement_id.
    Creazione automatica alla prima scrittura: il chiamante
    non deve pre-creare l'evidence prima di scrivere un nodo.
    """

    def __init__(self, evidences: dict[str, AssetEvidence] | None = None):
        self._evidences: dict[str, AssetEvidence] = dict(evidences or {})

    @property
    def evidences(self) -> MappingProxyType[str, AssetEvidence]:
        return MappingProxyType(self._evidences)

    def get_evidence(self, requirement_id: str) -> AssetEvidence | None:
        return self._evidences.get(requirement_id)

    def set_node_choice(self, requirement_id: str,
                        node_id: str, value: bool) -> None:
        evidence = self._evidences.get(requirement_id)
        if evidence is None:
            evidence = AssetEvidence(requirement_id=requirement_id)
        self._evidences[requirement_id] = evidence.with_node_choice(node_id, value)

    def set_justification(self, requirement_id: str,
                          justification: str) -> None:
        evidence = self._evidences.get(requirement_id)
        if evidence is None:
            evidence = AssetEvidence(requirement_id=requirement_id)
        self._evidences[requirement_id] = evidence.with_justification(justification)


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