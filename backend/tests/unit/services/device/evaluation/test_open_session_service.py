import pytest
from unittest.mock import MagicMock

from core.ports.inbound.evaluation.evaluation_session.open_evaluation_session_use_case import (
    OpenEvaluationSessionCommand,
)
from core.ports.inbound.evaluation.exceptions import OpenEvaluationSessionFailure
from core.ports.outbound.device.exceptions import DeviceNotFoundError
from core.ports.outbound.compliance_standard.exceptions import StandardNotFoundError
from core.ports.outbound.evaluation.exceptions import EvaluationSessionOpenError
from core.services.evaluation.evaluation_session.open_evaluation_session_service import OpenEvaluationSessionService


@pytest.fixture
def mock_session_coordinator():
    return MagicMock()


@pytest.fixture
def mock_create_session_port():
    return MagicMock()


@pytest.fixture
def mock_find_device_port():
    return MagicMock()


@pytest.fixture
def mock_find_standard_port():
    return MagicMock()


@pytest.fixture
def service(
    mock_session_coordinator,
    mock_create_session_port,
    mock_find_device_port,
    mock_find_standard_port,
):
    return OpenEvaluationSessionService(
        session_coordinator=mock_session_coordinator,
        create_session_port=mock_create_session_port,
        find_device_port=mock_find_device_port,
        find_standard_port=mock_find_standard_port,
    )


@pytest.fixture
def command():
    return OpenEvaluationSessionCommand(device_id="DEV-1")


def _setup_happy_path(
    mock_session_coordinator,
    mock_find_device_port,
    mock_find_standard_port,
    mock_create_session_port,
):
    mock_session_coordinator.can_open_session.return_value = True

    mock_device = MagicMock()
    mock_device.id = "DEV-1"
    mock_device.standard_id = "STD-1"
    mock_find_device_port.find_by_id.return_value = mock_device

    mock_standard = MagicMock()
    mock_standard.id = "STD-1"
    mock_find_standard_port.find_standard.return_value = mock_standard

    mock_session = MagicMock()
    mock_session.session_id = "SESSION-123"
    mock_create_session_port.create_evaluation_session.return_value = mock_session

    return mock_device, mock_standard, mock_session


class TestOpenEvaluationSessionSuccess:

    def test_returns_session_id(
        self, service, command,
        mock_session_coordinator, mock_find_device_port,
        mock_find_standard_port, mock_create_session_port,
    ):
        """
        Dato un dispositivo esistente e l'assenza di sessioni attive (Given),
        quando viene richiesto l'avvio di una nuova valutazione (When),
        allora il servizio deve restituire l'ID univoco della sessione appena creata (Then).
        """
        _, _, mock_session = _setup_happy_path(
            mock_session_coordinator, mock_find_device_port,
            mock_find_standard_port, mock_create_session_port,
        )

        result = service.open_evaluation_session(command)

        assert result == "SESSION-123"

    def test_checks_can_open_session(
        self, service, command,
        mock_session_coordinator, mock_find_device_port,
        mock_find_standard_port, mock_create_session_port,
    ):
        """
        Dato un comando di apertura sessione (Given),
        quando il servizio viene eseguito (When),
        allora deve consultare preventivamente il coordinatore per verificare se le politiche di sistema consentono l'apertura (Then).
        """
        _setup_happy_path(
            mock_session_coordinator, mock_find_device_port,
            mock_find_standard_port, mock_create_session_port,
        )

        service.open_evaluation_session(command)

        mock_session_coordinator.can_open_session.assert_called_once()

    def test_finds_device_by_id(
        self, service, command,
        mock_session_coordinator, mock_find_device_port,
        mock_find_standard_port, mock_create_session_port,
    ):
        """
        Dato un ID dispositivo nel comando (Given),
        quando la validazione della sessione ha esito positivo (When),
        allora il servizio deve recuperare l'anagrafica completa del dispositivo dal repository (Then).
        """
        _setup_happy_path(
            mock_session_coordinator, mock_find_device_port,
            mock_find_standard_port, mock_create_session_port,
        )

        service.open_evaluation_session(command)

        mock_find_device_port.find_by_id.assert_called_once_with("DEV-1")

    def test_finds_standard_by_device_standard_id(
        self, service, command,
        mock_session_coordinator, mock_find_device_port,
        mock_find_standard_port, mock_create_session_port,
    ):
        """
        Dato un dispositivo associato a uno standard specifico (Given),
        quando il dispositivo viene caricato (When),
        allora il servizio deve recuperare la definizione dello standard corrispondente per la sessione (Then).
        """
        mock_device, _, _ = _setup_happy_path(
            mock_session_coordinator, mock_find_device_port,
            mock_find_standard_port, mock_create_session_port,
        )

        service.open_evaluation_session(command)

        mock_find_standard_port.find_standard.assert_called_once_with(mock_device.standard_id)

    def test_creates_session_with_device_and_standard(
        self, service, command,
        mock_session_coordinator, mock_find_device_port,
        mock_find_standard_port, mock_create_session_port,
    ):
        """
        Dati il dispositivo e lo standard di conformità recuperati correttamente (Given),
        quando il processo di apertura prosegue (When),
        allora il servizio deve invocare la creazione della sessione di valutazione aggregando entrambi gli oggetti di dominio (Then).
        """
        mock_device, mock_standard, _ = _setup_happy_path(
            mock_session_coordinator, mock_find_device_port,
            mock_find_standard_port, mock_create_session_port,
        )

        service.open_evaluation_session(command)

        mock_create_session_port.create_evaluation_session.assert_called_once_with(
            standard=mock_standard, device=mock_device,
        )


class TestOpenEvaluationSessionFailures:

    def test_raises_failure_when_session_already_active(
        self, service, command, mock_session_coordinator,
    ):
        """
        Dato un sistema in cui è già presente una sessione attiva (Given),
        quando si tenta di aprirne una nuova (When),
        allora il servizio deve sollevare un'eccezione OpenEvaluationSessionFailure segnalando il conflitto (Then).
        """
        mock_session_coordinator.can_open_session.return_value = False

        with pytest.raises(OpenEvaluationSessionFailure, match="sessione attiva"):
            service.open_evaluation_session(command)

    def test_raises_failure_when_device_not_found(
        self, service, command,
        mock_session_coordinator, mock_find_device_port,
    ):
        """
        Dato un ID dispositivo non presente a database (Given),
        quando si tenta di avviare la sessione (When),
        allora il servizio deve intercettare l'errore di ricerca e sollevare un fallimento specifico per dispositivo non trovato (Then).
        """
        mock_session_coordinator.can_open_session.return_value = True
        mock_find_device_port.find_by_id.side_effect = DeviceNotFoundError("non trovato")

        with pytest.raises(OpenEvaluationSessionFailure, match="dispositivo"):
            service.open_evaluation_session(command)

    def test_raises_failure_when_standard_not_found(
        self, service, command,
        mock_session_coordinator, mock_find_device_port,
        mock_find_standard_port,
    ):
        """
        Dato un dispositivo che referenzia uno standard inesistente (Given),
        quando il servizio tenta il caricamento dello standard (When),
        allora deve sollevare una OpenEvaluationSessionFailure riportando l'errore di configurazione dello standard (Then).
        """
        mock_session_coordinator.can_open_session.return_value = True

        mock_device = MagicMock()
        mock_device.standard_id = "STD-999"
        mock_find_device_port.find_by_id.return_value = mock_device

        mock_find_standard_port.find_standard.side_effect = StandardNotFoundError("non trovato")

        with pytest.raises(OpenEvaluationSessionFailure, match="standard"):
            service.open_evaluation_session(command)

    def test_raises_failure_when_create_session_fails(
        self, service, command,
        mock_session_coordinator, mock_find_device_port,
        mock_find_standard_port, mock_create_session_port,
    ):
        """
        Dato un errore tecnico imprevisto durante l'inizializzazione della sessione (Given),
        quando la porta di creazione fallisce (When),
        allora il servizio deve catturare l'errore tecnico e rilanciare una OpenEvaluationSessionFailure (Then).
        """
        _setup_happy_path(
            mock_session_coordinator, mock_find_device_port,
            mock_find_standard_port, mock_create_session_port,
        )
        mock_create_session_port.create_evaluation_session.side_effect = (
            EvaluationSessionOpenError("errore creazione")
        )

        with pytest.raises(OpenEvaluationSessionFailure, match="apertura"):
            service.open_evaluation_session(command)

    def test_does_not_find_device_when_session_cannot_open(
        self, service, command,
        mock_session_coordinator, mock_find_device_port,
    ):
        """
        Dato un sistema già impegnato (Given),
        quando la pre-validazione fallisce (When),
        allora il servizio deve interrompersi immediatamente senza tentare inutili ricerche sul database dei dispositivi (Then).
        """
        mock_session_coordinator.can_open_session.return_value = False

        with pytest.raises(OpenEvaluationSessionFailure):
            service.open_evaluation_session(command)

        mock_find_device_port.find_by_id.assert_not_called()