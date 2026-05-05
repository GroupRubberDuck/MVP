def is_blank(value: str) -> bool:
    """Verifica che una stringa non sia vuota o composta solo da spazi."""
    return bool(value and value.strip())


def key_exists(dictionary: dict, key: str) -> bool:
    """Verifica che una chiave sia presente in un dizionario."""
    return key in dictionary