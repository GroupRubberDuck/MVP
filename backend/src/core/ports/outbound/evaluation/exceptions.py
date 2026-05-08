class EvaluationSessionError(Exception):
    """Errore generico relativo alla sessione di valutazione."""
    pass

class EvaluationSessionAlreadyExistsError(EvaluationSessionError):
    """Esiste già una sessione di valutazione attiva."""
    pass

class EvaluationSessionNotFoundError(EvaluationSessionError):
    """Nessuna sessione attiva trovata per l'ID fornito."""
    pass

class EvaluationSessionSaveError(EvaluationSessionError):
    """Errore durante il salvataggio della sessione di valutazione."""
    pass

# class AssetNotInSessionError(EvaluationSessionError):
#     """L'asset richiesto non è presente nella sessione."""
#     """Impossibile trovare la sessione"""
#     pass