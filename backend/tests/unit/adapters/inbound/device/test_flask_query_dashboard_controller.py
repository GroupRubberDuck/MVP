import pytest
from unittest.mock import MagicMock, patch
from flask import Flask, blueprints

from adapters.inbound.device.flask_query_dashboard_controller import (
    FlaskQueryDashboardController,
    DeviceDashboardDTO,
    AssetSummaryDTO,
)
from core.ports.inbound.device.get_device_evaluation_detail_use_case import (
    GetDeviceEvaluationDetailCommand,
)
from core.ports.inbound.evaluation.exceptions import GetEvaluationDetailFailure
from core.domain.evaluation_standard.evaluation_state import EvaluationState
from core.domain.evaluation_object.asset.asset_type import AssetType

SESSION_ID = "session-1"
DEVICE_ID = "device-1"
BASE_URL = f"/sessions/{SESSION_ID}/devices/{DEVICE_ID}/dashboard"
PATCH_RENDER = (
    "adapters.inbound.device.flask_query_dashboard_controller.render_template"
)


def _make_mock_asset(
    asset_id: str = "asset-1",
    verdict: EvaluationState = EvaluationState.PASS,
) -> MagicMock:
    asset = MagicMock()
    asset.asset_id = asset_id
    asset.name = "Test Asset"
    asset.asset_type = AssetType.SECURITY
    asset.verdict = verdict
    return asset


def _make_mock_detail(assets: list[MagicMock] | None = None) -> MagicMock:
    detail = MagicMock()
    detail.device_id = DEVICE_ID
    detail.name = "Test Device"
    detail.operating_system = "Windows 10"
    detail.description = "A description"
    detail.verdict = EvaluationState.PASS
    detail.asset_details = assets if assets is not None else [_make_mock_asset()]
    return detail


@pytest.fixture(scope="module")
def app_and_mock() -> tuple[Flask, MagicMock]:
    mock_use_case = MagicMock()
    controller = FlaskQueryDashboardController(
        get_device_evaluation_detail_use_case=mock_use_case
    )
    flask_app = Flask(__name__)
    blueprint = blueprints.Blueprint("device_dashboard", __name__)
    controller.register_routes(blueprint)
    flask_app.register_blueprint(blueprint)
    flask_app.config["TESTING"] = True
    return flask_app, mock_use_case


@pytest.fixture()
def app(app_and_mock: tuple[Flask, MagicMock]) -> tuple[Flask, MagicMock]:
    flask_app, mock_use_case = app_and_mock
    mock_use_case.reset_mock()
    mock_use_case.get_device_evaluation_detail.side_effect = None
    return flask_app, mock_use_case


class TestFlaskQueryDashboardController:
    def test_risponde_200_caso_felice(self, app: tuple[Flask, MagicMock]) -> None:
        """
        Dato un ID di sessione e un ID device validi che restituiscono un dettaglio valutativo (Given),
        quando l'utente richiede la dashboard del dispositivo (When),
        allora il controller deve restituire uno status code 200 OK (Then).
        """
        flask_app, mock_use_case = app
        mock_use_case.get_device_evaluation_detail.return_value = _make_mock_detail()
        with patch(PATCH_RENDER, return_value=""):
            with flask_app.test_client() as client:
                response = client.get(BASE_URL)
        assert response.status_code == 200

    def test_chiama_use_case_una_volta(self, app: tuple[Flask, MagicMock]) -> None:
        """
        Dati un ID di sessione e un ID device validi (Given),
        quando viene invocata la rotta della dashboard (When),
        allora lo use case delegato al recupero dei dettagli deve essere chiamato esattamente una volta (Then).
        """
        flask_app, mock_use_case = app
        mock_use_case.get_device_evaluation_detail.return_value = _make_mock_detail()
        with patch(PATCH_RENDER, return_value=""):
            with flask_app.test_client() as client:
                client.get(BASE_URL)
        mock_use_case.get_device_evaluation_detail.assert_called_once()

    def test_command_ha_i_campi_corretti(self, app: tuple[Flask, MagicMock]) -> None:
        """
        Dati un session_id e un device_id passati attraverso i parametri dell'URL (Given),
        quando viene effettuata la richiesta per la dashboard (When),
        allora i parametri estratti devono essere mappati correttamente all'interno del Command per lo use case (Then).
        """
        flask_app, mock_use_case = app
        mock_use_case.get_device_evaluation_detail.return_value = _make_mock_detail()
        with patch(PATCH_RENDER, return_value=""):
            with flask_app.test_client() as client:
                client.get(BASE_URL)
        command: GetDeviceEvaluationDetailCommand = (
            mock_use_case.get_device_evaluation_detail.call_args[0][0]
        )
        assert command.session_id == SESSION_ID
        assert command.device_id == DEVICE_ID

    def test_use_case_failure_risponde_404(self, app: tuple[Flask, MagicMock]) -> None:
        """
        Dato uno scenario in cui lo use case lancia un'eccezione GetEvaluationDetailFailure per device inesistente (Given),
        quando viene richiesta la dashboard del dispositivo (When),
        allora il controller deve intercettare l'errore e restituire uno status code 404 Not Found (Then).
        """
        flask_app, mock_use_case = app
        mock_use_case.get_device_evaluation_detail.side_effect = (
            GetEvaluationDetailFailure("not found")
        )
        with patch(PATCH_RENDER, return_value=""):
            with flask_app.test_client() as client:
                response = client.get(BASE_URL)
        assert response.status_code == 404

    def test_use_case_failure_usa_template_errore(
        self, app: tuple[Flask, MagicMock]
    ) -> None:
        """
        Dato un fallimento nel recupero dei dettagli valutativi del dispositivo (Given),
        quando la rotta gestisce l'eccezione (When),
        allora il controller deve renderizzare il template HTML specifico per gli errori 404 passando il relativo messaggio (Then).
        """
        flask_app, mock_use_case = app
        mock_use_case.get_device_evaluation_detail.side_effect = (
            GetEvaluationDetailFailure("not found")
        )
        with patch(PATCH_RENDER, return_value="") as mock_render:
            with flask_app.test_client() as client:
                client.get(BASE_URL)
        assert mock_render.call_args[0][0] == "errors/404.html"
        assert "message" in mock_render.call_args.kwargs

    def test_usa_template_dashboard(self, app: tuple[Flask, MagicMock]) -> None:
        """
        Dati dei risultati validi restituiti dalla business logic (Given),
        quando la dashboard viene elaborata con successo (When),
        allora il controller deve utilizzare il template 'layouts/device/dashboard.html' per la renderizzazione (Then).
        """
        flask_app, mock_use_case = app
        mock_use_case.get_device_evaluation_detail.return_value = _make_mock_detail()
        with patch(PATCH_RENDER, return_value="") as mock_render:
            with flask_app.test_client() as client:
                client.get(BASE_URL)
        assert mock_render.call_args[0][0] == "layouts/device/dashboard.html"

    def test_mapping_campi_device_nel_dto(self, app: tuple[Flask, MagicMock]) -> None:
        """
        Dato un oggetto di dettaglio restituito in uscita dallo use case (Given),
        quando il controller prepara la vista per il front-end (When),
        allora i dati anagrafici e di stato del device devono essere mappati correttamente in un DeviceDashboardDTO (Then).
        """
        flask_app, mock_use_case = app
        mock_detail = _make_mock_detail()
        mock_use_case.get_device_evaluation_detail.return_value = mock_detail

        captured: dict = {}

        def capture(template_name: str, **kwargs: object) -> str:
            captured.update(kwargs)
            return ""

        with patch(PATCH_RENDER, side_effect=capture):
            with flask_app.test_client() as client:
                client.get(BASE_URL)

        dto: DeviceDashboardDTO = captured["dashboard"]
        assert dto.device_id == mock_detail.device_id
        assert dto.device_name == mock_detail.name
        assert dto.operating_system == mock_detail.operating_system
        assert dto.description == mock_detail.description
        assert dto.aggregate_status == mock_detail.verdict

    def test_mapping_asset_list(self, app: tuple[Flask, MagicMock]) -> None:
        """
        Dato un dettaglio valutativo contenente una lista di asset analizzati (Given),
        quando i dati vengono strutturati per il template della dashboard (When),
        allora l'elenco degli asset deve essere mappato all'interno del DTO rispettando id, nomi, tipi e verdetti (Then).
        """
        flask_app, mock_use_case = app
        mock_asset = _make_mock_asset(asset_id="asset-99", verdict=EvaluationState.FAIL)
        mock_use_case.get_device_evaluation_detail.return_value = _make_mock_detail(
            assets=[mock_asset]
        )

        captured: dict = {}

        def capture(template_name: str, **kwargs: object) -> str:
            captured.update(kwargs)
            return ""

        with patch(PATCH_RENDER, side_effect=capture):
            with flask_app.test_client() as client:
                client.get(BASE_URL)

        dto: DeviceDashboardDTO = captured["dashboard"]
        assert len(dto.asset_list) == 1
        asset_dto: AssetSummaryDTO = dto.asset_list[0]
        assert asset_dto.asset_id == "asset-99"
        assert asset_dto.name == mock_asset.name
        assert asset_dto.type == AssetType.SECURITY
        assert asset_dto.aggregate_status == EvaluationState.FAIL
