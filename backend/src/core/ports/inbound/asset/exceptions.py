class AssetFailure(Exception):
    """Errore generico relativo agli asset."""
    pass

class DeleteAssetFailure(AssetFailure):
    """Impossibile rimuovere l'asset."""
    pass

class GetAssetDetailFailure(AssetFailure):
    """L'asset detail non può essere recuperato (sessione non trovata o asset non presente)."""
    pass

class GetAssetAnagraphicFailure(Exception):
    """L'anagrafica dell'asset non può essere recuperata (sessione non trovata o asset non presente)."""
    pass
class UpdateAssetFailure(Exception):
    """Impossibile aggiornare l'asset"""
    pass

class CreateAssetFailure(AssetFailure):
    """Impossibile creare l'asset."""
    pass
