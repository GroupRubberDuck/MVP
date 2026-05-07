class SessionNotFoundError(Exception):
    """Nessuna sessione attiva trovata per l'ID fornito."""
    pass


class AssetNotInSessionError(Exception):
    """L'asset richiesto non è presente nella sessione."""
    pass