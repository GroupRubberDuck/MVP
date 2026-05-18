class DatabaseError(Exception):
    """Errore base per problemi con il database."""

    pass


class DatabaseConnectionError(DatabaseError):
    """MongoDB non raggiungibile."""

    pass


class DatabaseNotFoundError(DatabaseError):
    """Il database richiesto non esiste sul server."""

    pass
