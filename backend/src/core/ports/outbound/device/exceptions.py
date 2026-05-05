class DeviceNotFoundError(Exception):
    """Il device richiesto non esiste nello storage."""
    pass
 
 
class DuplicateDeviceError(Exception):
    """Un device con lo stesso id è già presente nello storage."""
    pass
 
