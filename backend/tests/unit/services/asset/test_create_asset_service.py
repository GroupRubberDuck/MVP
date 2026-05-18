import pytest
from unittest.mock import MagicMock
from core.services.asset.create_asset_service import (
    CreateAssetService,
    CreateAssetCommand,
)
from core.domain.evaluation_object.asset.asset_type import AssetType
from core.domain.evaluation_object.device import Device
from core.domain.evaluation_standard.compliance_standard import ComplianceStandard
from core.domain.session.evaluation_session import EvaluationSession


# fixtures


@pytest.fixture
def device():
    return Device.create(
        device_id="device-1",
        standard_id="standard-1",
        name="Test Device",
        os="Linux",
        description="Device di test",
    )


@pytest.fixture
def standard():
    return ComplianceStandard(
        standard_id="standard-1",
        name="Standard di test",
        version_number="1.0",
        requirements=[],
    )


@pytest.fixture
def session(device, standard):
    return EvaluationSession(session_id="session-1", standard=standard, device=device)


@pytest.fixture
def get_evaluation_session_mock(session):
    mock = MagicMock()
    mock.get_evaluation_session.return_value = session
    return mock


@pytest.fixture
def save_evaluation_session_mock():
    return MagicMock()


@pytest.fixture
def service(get_evaluation_session_mock, save_evaluation_session_mock):
    return CreateAssetService(
        get_evaluation_session=get_evaluation_session_mock,
        save_evaluation_session=save_evaluation_session_mock,
    )


@pytest.fixture
def valid_command():
    return CreateAssetCommand(
        name="Router",
        device_id="device-1",
        asset_type=AssetType.NETWORK,
        description="Router di test",
        session_id="session-1",
    )


# caso nominale


def test_create_asset_returns_true(service, valid_command):
    """
    Dato un comando di creazione asset valido (Given),
    quando il servizio esegue la creazione (When),
    allora deve restituire una stringa non vuota che rappresenta l'ID dell'asset creato (Then).
    """
    result = service.create_asset(valid_command)
    assert isinstance(result, str)
    assert len(result) > 0


def test_create_asset_aggiunge_asset_al_device(service, valid_command, session):
    """
    Dato un comando per aggiungere un nuovo asset (Given),
    quando il servizio viene invocato (When),
    allora l'asset deve essere effettivamente inserito nella collezione degli asset del dispositivo all'interno della sessione (Then).
    """
    # Il device deve avere esattamente 1 asset dopo la creazione
    service.create_asset(valid_command)
    assert len(session.device.assets) == 1


def test_create_asset_nome_corretto(service, valid_command, session):
    """
    Dato un comando di creazione che specifica un nome per l'asset (Given),
    quando il servizio processa la richiesta (When),
    allora l'asset creato e aggiunto al dispositivo deve avere esattamente quel nome anagrafico (Then).
    """
    # Il nome dell'asset deve corrispondere a quello del command
    service.create_asset(valid_command)
    asset = list(session.device.assets.values())[0]
    assert asset.anagraphic.name == "Router"


def test_create_asset_tipo_corretto(service, valid_command, session):
    """
    Dato un comando che definisce una specifica tipologia di asset (Given),
    quando l'asset viene generato (When),
    allora il tipo dell'asset (es. NETWORK) deve corrispondere a quello indicato nel comando (Then).
    """
    # Il tipo dell'asset deve corrispondere a quello del command
    service.create_asset(valid_command)
    asset = list(session.device.assets.values())[0]
    assert asset.anagraphic.asset_type == AssetType.NETWORK


def test_create_asset_salva_sessione(
    service, valid_command, save_evaluation_session_mock, session
):
    """
    Dato l'inserimento con successo di un nuovo asset nel dominio (Given),
    quando il servizio termina la logica di business (When),
    allora deve invocare il salvataggio della sessione aggiornata per garantirne la persistenza (Then).
    """
    # La sessione aggiornata deve essere persistita esattamente una volta
    service.create_asset(valid_command)
    save_evaluation_session_mock.save_evaluation_session.assert_called_once_with(
        session
    )


# casi di errore
def test_create_asset_sessione_non_trovata(save_evaluation_session_mock):
    """
    Dato un comando con un ID sessione inesistente o non caricato in cache (Given),
    quando il servizio tenta di recuperare la sessione (When),
    allora deve propagare l'eccezione KeyError per segnalare l'assenza della risorsa (Then).
    """
    # Se il session_id non esiste in cache deve propagare KeyError
    get_evaluation_session_mock = MagicMock()
    get_evaluation_session_mock.get_evaluation_session.side_effect = KeyError(
        "Sessione non trovata"
    )
    service = CreateAssetService(
        get_evaluation_session=get_evaluation_session_mock,
        save_evaluation_session=save_evaluation_session_mock,
    )
    command = CreateAssetCommand(
        name="Router",
        device_id="device-1",
        asset_type=AssetType.NETWORK,
        description="",
        session_id="session-inesistente",
    )
    with pytest.raises(KeyError):
        service.create_asset(command)
