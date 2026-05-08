class DeviceNotFoundError(Exception):
    """Il device richiesto non esiste nello storage."""
    pass
 
 
class DuplicateDeviceError(Exception):
    """Un device con lo stesso id è già presente nello storage."""
    pass


class DeviceImportError(Exception):
    """Errore durante l'importazione di un device."""
    pass

class InvalidFileFormatError(DeviceImportError):
    """File malformato o non parsabile."""
    pass


class MissingDeviceFieldError(DeviceImportError):
    """Campo obbligatorio assente o vuoto nel file."""
    pass


class InvalidAssetTypeError(DeviceImportError):
    """Valore asset_type non riconosciuto."""
    pass


class EmptyFileError(DeviceImportError):
    """File privo di contenuto."""
    pass

class FileTooLargeError(DeviceImportError):
    pass


class DeviceExportError(Exception):
    """Errore durante l'esportazione di un device."""
    pass

class UnsupportedExportFormatError(DeviceExportError):
    """Formato di esportazione non supportato."""
    pass