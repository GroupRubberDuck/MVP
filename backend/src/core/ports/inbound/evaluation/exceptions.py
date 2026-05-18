class InsertJustificationFailure(Exception):
    """Eccezione sollevata quando la giustificazione non può essere impostata."""

    pass


class EvaluateNodeFailure(Exception):
    """Eccezione sollevata quando la valutazione di un nodo decisionale fallisce per regole di business."""


class CommitSessionFailure(Exception):
    """Eccezione sollevata quando il commit della sessione fallisce per logica di business o problemi infrastrutturali."""

    pass


class OpenEvaluationSessionFailure(Exception):
    """Eccezione sollevata quando l'apertura di una sessione di valutazione fallisce per logica di business o problemi infrastrutturali."""

    pass


class GetEvaluationDetailFailure(Exception):
    """Lanciata quando non è possibile recuperare il dettaglio della valutazione."""

    pass
