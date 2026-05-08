import pytest
from core.domain.session.session_handler import SessionHandler


@pytest.fixture
def handler() -> SessionHandler:
    return SessionHandler()


def test_can_open_session_when_no_active_session_exists(handler: SessionHandler):
    result = handler.can_open_session(
        active_session_exists=False
    )
    assert result is True


def test_cannot_open_session_when_active_session_exists(handler: SessionHandler):
    result = handler.can_open_session(active_session_exists=True)
    assert result is False


def test_cannot_open_standard_editing_when_active_session_exists(
    handler: SessionHandler,
):
    result = handler.can_open_session(active_session_exists=True)
    assert result is False
