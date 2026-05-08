from core.domain.shared.exceptions import DomainError

class DuplicateAssetError(DomainError):
    pass

class AssetNotFoundError(DomainError):
    pass

class EvidenceNotFoundError(DomainError):
    pass

class RequirementAlreadyExistsError(DomainError):
    pass

