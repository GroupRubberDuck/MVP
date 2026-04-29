# ── Eccezioni di dominio ──────────────────────────────

class DuplicateAssetError(Exception):
    pass

class AssetNotFoundError(Exception):
    pass

class RequirementNotFoundError(Exception):
    pass

class RequirementAlreadyExistsError(Exception):
    pass

