class AssetOperationFailure(Exception):
    """Base exception for asset operations."""

    pass


class AssetCreationFailure(AssetOperationFailure):
    """Exception raised when asset creation fails."""

    pass
