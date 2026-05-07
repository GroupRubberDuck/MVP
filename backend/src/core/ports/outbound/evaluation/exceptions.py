class EvaluationSessionNotFoundError(Exception):
    """Nessuna sessione attiva trovata per l'ID fornito."""
    pass

class EvaluationSessionSaveError(Exception):
    """Errore durante il salvataggio della sessione di valutazione."""
    pass

class AssetNotInSessionError(Exception):
    """L'asset richiesto non è presente nella sessione."""
    pass