class ImportDeviceFailure(Exception):
    """eccezione propagata durante il fallimento dell'importazione di 
    un device tramite uno use case."""
    pass

class DeviceRegistrationFailure(Exception):
    """Errore durante la registrazione di un device."""
    pass

class DeviceNotFoundFailure(Exception):
    """Errore durante la ricerca di un device non esistente."""
    pass