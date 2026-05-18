from core.domain.shared.exceptions import DomainError


class CycleDetectedError(DomainError):
    pass


class MissingDecisionTreeError(DomainError):
    pass


class RequirementNotFoundError(DomainError):
    pass
