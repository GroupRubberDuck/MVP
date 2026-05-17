import pytest
from unittest.mock import Mock
from flask import Flask

from core.domain.evaluation_object.device_summary import DeviceSummary

from core.services.device.get_device_list_service import GetDeviceListService
from adapters.inbound.device.flask_query_device_controller import FlaskQueryDeviceController


# ── Fixtures ──


@pytest.fixture
def mock_find_all_port():
    return Mock()


@pytest.fixture
def mock_find_device_port():
    return Mock()


@pytest.fixture
def mock_get_device_list_use_case():
    return Mock()


@pytest.fixture
def mock_get_device_detail_use_case():
    return Mock()


@pytest.fixture
def mock_get_compliance_standard_use_case():
    return Mock()


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(
    app,
    mock_get_device_list_use_case,
    mock_get_device_detail_use_case,
    mock_get_compliance_standard_use_case,
):
    from flask import Blueprint

    controller = FlaskQueryDeviceController(
        get_device_list_use_case=mock_get_device_list_use_case,
        get_device_detail_use_case=mock_get_device_detail_use_case,
        get_compliance_standard_use_case=mock_get_compliance_standard_use_case,
    )
    bp = Blueprint("devices", __name__)
    controller.register_routes(bp)
    app.register_blueprint(bp)

    return app.test_client()



# ── GetDeviceListService ──


class TestGetDeviceListService:

    def test_returns_list_from_port(self, mock_find_all_port):
        """
        Dati uno o più dispositivi registrati nel sistema (Given),
        quando viene richiesto il recupero dell'elenco dei dispositivi (When),
        allora il servizio deve interrogare la porta di output e restituire una lista di oggetti DeviceSummary correttamente popolati (Then).
        """
        summaries = [
            DeviceSummary(
                device_id="D-1",
                name="Device 1",
                os="Linux",
                description="Test",
                compliance_standard_id="STD-1",
            ),
            DeviceSummary(
                device_id="D-2",
                name="Device 2",
                os="Windows",
                description="Test",
                compliance_standard_id="STD-1",
            ),
        ]
        mock_find_all_port.find_all.return_value = summaries

        service = GetDeviceListService(mock_find_all_port)
        result = service.get_device_list()

        assert len(result) == 2
        assert result[0].device_id == "D-1"
        assert result[1].device_id == "D-2"
        mock_find_all_port.find_all.assert_called_once()

    def test_returns_empty_list(self, mock_find_all_port):
        """
        Dato un sistema privo di dispositivi registrati (Given),
        quando viene invocata la richiesta dell'elenco (When),
        allora il servizio deve restituire una lista vuota senza sollevare eccezioni (Then).
        """
        mock_find_all_port.find_all.return_value = []

        service = GetDeviceListService(mock_find_all_port)
        result = service.get_device_list()

        assert result == []
