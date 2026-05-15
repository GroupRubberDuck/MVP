import pytest
from unittest.mock import Mock, patch
from flask import Flask, Blueprint

from adapters.inbound.device.flask_write_device_controller import FlaskWriteDeviceController
from core.ports.inbound.device.exceptions import (
    CreateDeviceFailure,
    UpdateDeviceFailure,
    DeleteDeviceFailure,
)

@pytest.fixture
def mock_create_use_case():
    return Mock()


@pytest.fixture
def mock_update_use_case():
    return Mock()


@pytest.fixture
def mock_delete_use_case():
    return Mock()


@pytest.fixture
def client(mock_create_use_case, mock_update_use_case, mock_delete_use_case):
    app = Flask(__name__)
    app.config["TESTING"] = True

    controller = FlaskWriteDeviceController(
        create_device_use_case=mock_create_use_case,
        update_device_use_case=mock_update_use_case,
        delete_device_use_case=mock_delete_use_case,
    )
    bp = Blueprint("devices", __name__)
    controller.register_routes(bp)
    
    @bp.route("/devices/<device_id>", endpoint="get_device_detail", methods=["GET"])
    def dummy_get_device_detail(device_id):
        return "Dummy route"
    app.register_blueprint(bp)

    return app.test_client()


# ── Create Device ──


class TestCreateDevice:
    @patch("adapters.inbound.device.flask_write_device_controller.url_for")
    def test_returns_201_on_success(self,mock_url_for, client, mock_create_use_case):
        """
        Dati dei parametri validi per la registrazione di un nuovo dispositivo (Given),
        quando viene inviata una richiesta POST all'endpoint di creazione (When),
        allora il controller deve restituire uno status code 201 Created e l'ID del dispositivo generato (Then).
        """
        mock_create_use_case.create_device.return_value = "D-123"
        mock_url_for.return_value = "/devices/D-123"
        response = client.post(
            "/devices",
            json={
                "device_name": "Test",
                "device_os": "Linux",
                "device_description": "A device",
                "standard_id": "STD-001",
            },
        )
        assert response.status_code == 201
        assert response.get_json()["device_id"] == "D-123"

    def test_calls_use_case_with_correct_data(self, client, mock_create_use_case):
        """
        Dato un payload JSON corretto e completo di tutti i campi obbligatori (Given),
        quando il controller processa la richiesta di creazione (When),
        allora i parametri estratti dal body devono essere mappati correttamente nel Command e passati allo use case (Then).
        """
        mock_create_use_case.create_device.return_value = "D-123"
        client.post(
            "/devices",
            json={
                "device_name": "Test",
                "device_os": "Linux",
                "device_description": "A device",
                "standard_id": "STD-001",
            },
        )
        command = mock_create_use_case.create_device.call_args[0][0]
        assert command.device_name == "Test"
        assert command.device_os == "Linux"
        assert command.device_description == "A device"
        assert command.standard_id == "STD-001"

    def test_returns_400_when_body_is_none(self, client):
        """
        Data una richiesta POST in cui manca del tutto il payload JSON (Given),
        quando la richiesta raggiunge il controller (When),
        allora l'operazione deve essere interrotta restituendo uno status code 400 Bad Request (Then).
        """
        response = client.post("/devices", content_type="application/json")
        assert response.status_code == 400

    def test_returns_400_when_field_missing(self, client):
        """
        Dato un payload JSON in cui mancano uno o più campi obbligatori definiti da Pydantic (Given),
        quando il controller tenta di costruire il Command (When),
        allora deve intercettare l'errore di validazione e restituire uno status 400 Bad Request (Then).
        """
        response = client.post(
            "/devices",
            json={"device_name": "Test"},
        )
        assert response.status_code == 400

    def test_returns_error_on_create_failure(self, client, mock_create_use_case):
        """
        Dati in input che generano un conflitto logico (es. dispositivo duplicato) sollevando una CreateDeviceFailure (Given),
        quando lo use case tenta di salvare il record (When),
        allora il controller deve catturare l'eccezione e restituire uno status code 409 Conflict con il messaggio d'errore (Then).
        """
        mock_create_use_case.create_device.side_effect = CreateDeviceFailure("duplicato")
        response = client.post(
            "/devices",
            json={
                "device_name": "Test",
                "device_os": "Linux",
                "device_description": "A device",
                "standard_id": "STD-001",
            },
        )
        assert response.status_code == 409
        assert "duplicato" in response.get_json()["error"]


# ── Update Device ──


class TestUpdateDevice:

    def test_returns_200_on_success(self, client, mock_update_use_case):
        """
        Dato un ID dispositivo valido e un payload JSON contenente i dati aggiornati (Given),
        quando viene effettuata una richiesta PUT per aggiornare l'anagrafica (When),
        allora il controller deve applicare la modifica e restituire uno status code 200 OK (Then).
        """
        response = client.put(
            "/devices/D-1",
            json={
                "device_name": "Updated",
                "device_os": "Windows",
                "device_description": "Updated desc",
            },
        )
        assert response.status_code == 200

    def test_calls_use_case_with_correct_data(self, client, mock_update_use_case):
        """
        Dati dei parametri di aggiornamento estratti correttamente dall'URL e dal body della richiesta (Given),
        quando il controller delega l'operazione (When),
        allora l'ID e i nuovi dati devono corrispondere esattamente ai valori inseriti nel Command per lo use case (Then).
        """
        client.put(
            "/devices/D-1",
            json={
                "device_name": "Updated",
                "device_os": "Windows",
                "device_description": "Updated desc",
            },
        )
        command = mock_update_use_case.update_device.call_args[0][0]
        assert command.device_id == "D-1"
        assert command.device_name == "Updated"
        assert command.device_os == "Windows"
        assert command.device_description == "Updated desc"

    def test_returns_400_when_body_is_none(self, client):
        """
        Data una richiesta di aggiornamento priva di un corpo JSON valido (Given),
        quando l'operazione arriva al controller (When),
        allora deve essere immediatamente bloccata restituendo uno status code 400 Bad Request (Then).
        """
        response = client.put("/devices/D-1", content_type="application/json")
        assert response.status_code == 400

    def test_returns_400_when_field_missing(self, client):
        """
        Dato un payload JSON incompleto ricevuto per una rotta di aggiornamento (Given),
        quando la validazione del Command Pydantic fallisce (When),
        allora il controller deve intercettare l'errore e ritornare uno status code 400 Bad Request (Then).
        """
        response = client.put(
            "/devices/D-1",
            json={"device_name": "Updated"},
        )
        assert response.status_code == 400

    def test_returns_error_on_update_failure(self, client, mock_update_use_case):
        """
        Dato un ID dispositivo non presente nel database che provoca una UpdateDeviceFailure (Given),
        quando lo use case tenta di applicare la modifica (When),
        allora il controller deve gestire l'eccezione restituendo uno status code 404 Not Found con il dettaglio dell'errore (Then).
        """
        mock_update_use_case.update_device.side_effect = UpdateDeviceFailure("non trovato")
        response = client.put(
            "/devices/D-1",
            json={
                "device_name": "Updated",
                "device_os": "Windows",
                "device_description": "Updated desc",
            },
        )
        assert response.status_code == 404
        assert "non trovato" in response.get_json()["error"]


# ── Delete Device ──


class TestDeleteDevice:

    def test_returns_204_on_success(self, client, mock_delete_use_case):
        """
        Dato un ID di un dispositivo regolarmente registrato a sistema (Given),
        quando viene inviata una richiesta DELETE all'endpoint associato (When),
        allora il controller deve completare l'eliminazione e restituire uno status code 204 No Content (Then).
        """
        response = client.delete("/devices/D-1")
        assert response.status_code == 204

    def test_calls_use_case_with_correct_id(self, client, mock_delete_use_case):
        """
        Dato un ID di dispositivo estratto dai parametri dell'URL (Given),
        quando si attiva la richiesta di cancellazione (When),
        allora tale ID deve essere iniettato nel Command corretto e propagato allo use case di eliminazione (Then).
        """
        client.delete("/devices/D-1")
        command = mock_delete_use_case.delete_device.call_args[0][0]
        assert command.device_id == "D-1"

    def test_returns_error_on_delete_failure(self, client, mock_delete_use_case):
        """
        Data una richiesta di cancellazione per un ID che non esiste nel sistema o che non può essere eliminato (DeleteDeviceFailure) (Given),
        quando lo use case notifica il fallimento (When),
        allora il controller deve rispondere adeguatamente con uno status code 404 Not Found (Then).
        """
        mock_delete_use_case.delete_device.side_effect = DeleteDeviceFailure("non trovato")
        response = client.delete("/devices/D-1")
        assert response.status_code == 404
        assert "non trovato" in response.get_json()["error"]