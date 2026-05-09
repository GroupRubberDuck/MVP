class InsertJustificationFailure(Exception):
    """Eccezione sollevata quando la giustificazione non può essere impostata."""
    pass

class EvaluateNodeFailure(Exception):
    """Eccezione sollevata quando la valutazione di un nodo decisionale fallisce per regole di business."""
    pass