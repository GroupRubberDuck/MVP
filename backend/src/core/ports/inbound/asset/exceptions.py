class DeleteAssetFailure(Exception):
    """Impossibile rimuovere l'asset."""
    pass

class GetAssetDetailFailure(Exception):
    """L'asset detail non può essere recuperato (sessione non trovata o asset non presente)."""
    pass

class GetRequirementEvaluationDetailFailure(Exception):
    """Il dettaglio di valutazione del requisito non può essere recuperato
    (sessione non trovata, asset non presente o requisito non trovato)."""
    pass