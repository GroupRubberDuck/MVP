# ── Eccezioni di dominio ──────────────────────────────

class DuplicateAssetError(Exception):
    pass

class AssetNotFoundError(Exception):
    pass

class AnswerNotFoundError(Exception):
    pass

class RequirementAlreadyExistsError(Exception):
    pass

