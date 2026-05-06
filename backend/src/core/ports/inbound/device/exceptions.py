class ImportDeviceFailure(Exception):
    """eccezione propagata durante il fallimento dell'importazione di 
    un device tramite uno use case."""
    pass

class DeviceRegistrationFailure(Exception):
    """Errore durante la registrazione di un device."""
    pass

class UpdateDeviceFailure(Exception):
    """Il dispositivo non può essere aggiornato (non trovato o dati non validi)."""
    pass