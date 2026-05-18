import pytest


@pytest.hookimpl(optionalhook=True)
def pytest_json_runtest_metadata(item, call):
    if call.when == "setup":
        # --- 1. Estrazione Descrizione (Docstring) ---
        docstring = item.obj.__doc__
        descrizione = docstring.strip() if docstring else "Nessuna descrizione fornita."

        # --- 2. Etichettatura Automatica tramite Cartella ---
        # item.path è un oggetto Path, lo convertiamo in stringa per comodità
        percorso_file = str(item.path)

        if "/unit/" in percorso_file:
            tipo_test = "Unitario"
        elif "/integration/" in percorso_file:
            tipo_test = "Integrazione"
        else:
            tipo_test = "Altro"

        # Ritorniamo il dizionario che finirà nel JSON
        return {"descrizione": descrizione, "tipo_test": tipo_test}
