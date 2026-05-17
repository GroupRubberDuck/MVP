import pytest
from core.domain.session.session_handler import SessionHandler


@pytest.fixture
def handler() -> SessionHandler:
    return SessionHandler()


def test_can_open_session_when_no_active_session_exists(handler: SessionHandler):
    """
    Dato un sistema in cui non risultano sessioni di valutazione attualmente aperte (Given),
    quando viene verificata la possibilità di iniziare una nuova sessione (When),
    allora il gestore deve confermare che l'operazione è consentita restituendo True (Then).
    """
    result = handler.can_open_session(
        active_session_exists=False
    )
    assert result is True


def test_cannot_open_session_when_active_session_exists(handler: SessionHandler):
    """
    Dato uno stato del sistema in cui esiste già una sessione attiva (Given),
    quando si tenta di convalidare l'apertura di una seconda sessione concorrente (When),
    allora il gestore deve impedire l'operazione restituendo False (Then).
    """
    result = handler.can_open_session(active_session_exists=True)
    assert result is False


def test_cannot_open_standard_editing_when_active_session_exists(
    handler: SessionHandler,
):
    """
    Dato un contesto in cui una valutazione è in corso (Given),
    quando viene richiesta l'autorizzazione per procedere con l'apertura di una sessione (When),
    allora il sistema deve negare il permesso per garantire l'integrità dei dati e prevenire conflitti (Then).
    """
    result = handler.can_open_session(active_session_exists=True)
    assert result is False
