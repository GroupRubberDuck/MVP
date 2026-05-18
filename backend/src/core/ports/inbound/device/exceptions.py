class ImportDeviceFailure(Exception):
    """eccezione propagata durante il fallimento dell'importazione di
    un device tramite uno use case."""

    pass


class ExportDeviceFailure(Exception):
    """eccezione propagata durante il fallimento dell'esportazione di
    un device tramite uno use case."""

    pass


class DeviceRegistrationFailure(Exception):
    """Errore durante la registrazione di un device."""

    pass


class DeviceNotFoundFailure(Exception):
    """Errore durante la ricerca di un device non esistente."""

    pass


class UpdateDeviceFailure(Exception):
    """Il dispositivo non può essere aggiornato (non trovato o dati non validi)."""

    pass


class DeleteDeviceFailure(Exception):
    """Il dispositivo non può essere eliminato (non trovato o errore interno)."""


class CreateDeviceFailure(Exception):
    """Il dispositivo non può essere creato (dati non validi o errore di storage)."""

    pass
