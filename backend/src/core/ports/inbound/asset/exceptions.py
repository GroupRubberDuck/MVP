class DeleteAssetFailure(Exception):
    """Impossibile rimuovere l'asset."""
    pass

class GetAssetDetailFailure(Exception):
    """L'asset detail non può essere recuperato (sessione non trovata o asset non presente)."""
    pass

class UpdateAssetFailure(Exception):
    """Impossibile aggiornare l'asset"""
    pass
