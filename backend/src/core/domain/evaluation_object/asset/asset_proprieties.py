from types import MappingProxyType

from .asset_evidence import AssetEvidence


class AssetProprieties:
    """
    First Class Collection che gestisce le AssetEvidence
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