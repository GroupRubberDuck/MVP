import os
import string
import random

from flask import Flask, jsonify
from dotenv import load_dotenv

from infrastructure.database.connection import connect
from infrastructure.database.exceptions import DatabaseConnectionError

# Adapter outbound
from adapters.outbound.device.device_repository.mongo_device_repository import MongoDeviceAdapter
from adapters.outbound.compliance_standard.compliance_standard_repository.mongodb_compliance_standard_repository import MongoComplianceStandardAdapter

# Service
from core.services.device.get_device_list_service import GetDeviceListService
from core.services.device.get_device_detail_service import GetDeviceDetailService
from core.services.compliance_standard.get_compliance_standard_service import GetComplianceStandardService

# Controller (adapter inbound)
from adapters.inbound.device.flask_query_device_controller import FlaskQueryDeviceController

# Routes
from routes import register_routes, register_error_handlers

load_dotenv()


def create_app() -> Flask:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, 'backend', 'templates'),
        static_folder=os.path.join(base_dir, 'backend', 'static'),
    )
    app.secret_key = "".join(random.choices(string.ascii_letters + string.digits, k=32))

    # ── Database ──
    try:
        mongo_client, db = connect()
    except DatabaseConnectionError as e:
        app.logger.error(f"DB CONNECTION ERROR: {e}")
        _register_fallback_routes(app, str(e), 503)
        return app

    # ── Adapter outbound ──
    device_adapter = MongoDeviceAdapter(db["devices"])
    standard_adapter = MongoComplianceStandardAdapter(db["compliance_standards"])

    # ── Service ──
    get_device_list_service = GetDeviceListService(device_adapter)
    get_device_detail_service = GetDeviceDetailService(device_adapter)
    get_compliance_standard_service = GetComplianceStandardService(standard_adapter)

    # ── Controller (adapter inbound) ──
    query_device_controller = FlaskQueryDeviceController(
        get_device_list_use_case=get_device_list_service,
        get_device_detail_use_case=get_device_detail_service,
        get_compliance_standard_use_case=get_compliance_standard_service,
    )

    # ── Rotte ──
    register_routes(
        app,
        device_controllers=[query_device_controller],
    )
    register_error_handlers(app)

    # ── Health check ──
    _register_health_check(app, mongo_client, db)

    return app


def _register_health_check(app: Flask, mongo_client, db) -> None:
    @app.route("/health")
    def health():
        try:
            mongo_client.admin.command("ping")
            return jsonify({"status": "ok", "database": db.name}), 200
        except Exception as e:
            return jsonify({"status": "error", "detail": str(e)}), 503


def _register_fallback_routes(app: Flask, error: str, status: int) -> None:
    """Se il DB non è disponibile, ogni rotta risponde con l'errore."""

    @app.route("/health")
    def health_fallback():
        return jsonify({"status": "error", "detail": error}), status

    @app.errorhandler(404)
    def fallback_404(e):
        return jsonify({
            "error": "Servizio non disponibile",
            "detail": f"Database non accessibile: {error}",
        }), status