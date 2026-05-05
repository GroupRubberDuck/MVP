# ── Eccezioni di dominio ──────────────────────────────

class DuplicateAssetError(Exception):
    pass

class AssetNotFoundError(Exception):
    pass

class EvidenceNotFoundError(Exception):
    pass

class RequirementAlreadyExistsError(Exception):
    pass

