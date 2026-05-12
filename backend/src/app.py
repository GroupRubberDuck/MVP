import os
import string
import random

from flask import Flask, jsonify
from dotenv import load_dotenv

from infrastructure.database.connection import connect
from infrastructure.database.exceptions import DatabaseConnectionError

# --- Adapter outbound ---
from adapters.outbound.device.repository.mongo_device_repository import MongoDeviceAdapter
from adapters.outbound.compliance_standard.mongodb_compliance_standard_repository import MongoComplianceStandardAdapter
from adapters.outbound.device.importer.concrete_file_device_importer_factory import ConcreteFileDeviceImporterFactory
from adapters.outbound.device.exporter.concrete_file_device_exporter_factory import ConcreteFileDeviceExporterFactory
from adapters.outbound.report.pdf_report_generator import PdfReportGenerator
from adapters.outbound.evaluation.in_memory_evaluation_session_cache import InMemoryEvaluationSessionCache

# --- Domain ---
from core.domain.session.session_handler import SessionHandler
from core.domain.evaluation_engine.evaluation_engine import EvaluationEngine

# --- Service (Application Core) ---
# Device
from core.services.device.get_device_list_service import GetDeviceListService
from core.services.device.get_device_detail_service import GetDeviceDetailService
from core.services.device.create_device_service import CreateDeviceService
from core.services.device.update_device_service import UpdateDeviceService
from core.services.device.delete_device_service import DeleteDeviceService
from core.services.device.import_device_service import ImportDeviceService
from core.services.device.export_device_service import ExportDeviceService

# Asset
from core.services.asset.create_asset_service import CreateAssetService
from core.services.asset.update_asset_service import UpdateAssetService
from core.services.asset.delete_asset_service import DeleteAssetService

# Evaluation Services
from core.services.device.get_device_evaluation_detail_service import GetDeviceEvaluationDetailService
from core.services.evaluation.evaluation_session.session_coordinator import SessionCoordinator
from core.services.evaluation.evaluation_session.open_evaluation_session_service import OpenEvaluationSessionService
from core.services.evaluation.evaluation_session.close_evaluation_session_service import CloseEvaluationSessionService
from core.services.evaluation.evaluation_session.commit_evaluation_session_service import CommitEvaluationSessionService

# Report & Compliance
from core.services.report.generate_report_service import GenerateReportService
from core.services.compliance_standard.get_compliance_standard_service import GetComplianceStandardService

# --- Controller (Adapter inbound) ---
# Device
from adapters.inbound.device.flask_query_device_controller import FlaskQueryDeviceController
from adapters.inbound.device.flask_write_device_controller import FlaskWriteDeviceController 
from adapters.inbound.device.flask_import_device_controller import FlaskImportDeviceController
from adapters.inbound.device.flask_export_device_controller import FlaskExportDeviceController

# Asset
from adapters.inbound.asset.flask_write_asset_controller import FlaskWriteAssetController

# Evaluation & Report
from adapters.inbound.evaluation.evaluation_detail.flask_device_evaluation_detail_controller import FlaskDeviceEvaluationDetailController
from adapters.inbound.evaluation.evaluation_session_controller import EvaluationSessionController
from adapters.inbound.report.report_controller import FlaskExportReportController

# --- Routes ---
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
    report_generator_adapter = PdfReportGenerator()
    
    importer_factory = ConcreteFileDeviceImporterFactory()
    exporter_factory = ConcreteFileDeviceExporterFactory()

    session_cache_adapter = InMemoryEvaluationSessionCache()

    # ── Servizi (Application Core) ──
    
    session_handler = SessionHandler() 
    session_coordinator = SessionCoordinator(
        exist_port=session_cache_adapter,
        session_handler=session_handler
    )

    open_session_service = OpenEvaluationSessionService(
        session_coordinator=session_coordinator,
        create_session_port=session_cache_adapter,
        find_device_port=device_adapter,
        find_standard_port=standard_adapter
    )

    close_session_service = CloseEvaluationSessionService(
        delete_session_port=session_cache_adapter
    )

    commit_session_service = CommitEvaluationSessionService(
        get_evaluation_session_port=session_cache_adapter,
        save_device_port=device_adapter
    )

    get_device_list_service = GetDeviceListService(device_adapter)
    get_device_detail_service = GetDeviceDetailService(device_adapter)
    get_compliance_standard_service = GetComplianceStandardService(standard_adapter)
    
    evaluation_engine = EvaluationEngine()

    get_device_evaluation_detail_service = GetDeviceEvaluationDetailService(
        get_evaluation_session_port=session_cache_adapter,
        evaluation_engine=evaluation_engine
    )

    create_device_service = CreateDeviceService(device_adapter)
    update_device_service = UpdateDeviceService(device_adapter, device_adapter)
    delete_device_service = DeleteDeviceService(device_adapter)
    import_device_service = ImportDeviceService(importer_factory, device_adapter)
    export_device_service = ExportDeviceService(device_adapter, exporter_factory)
    
    # 7. CRUD Asset (AGGIORNATI CON I NOMI ESATTI DELLE TUE CLASSI)
    create_asset_service = CreateAssetService(
        get_evaluation_session=session_cache_adapter,
        save_evaluation_session=session_cache_adapter
    )
    
    update_asset_service = UpdateAssetService(
        get_evaluation_session_port=session_cache_adapter,
        save_evaluation_session_port=session_cache_adapter
    )
    
    delete_asset_service = DeleteAssetService(
        save_evaluation_session_port=session_cache_adapter,
        get_evaluation_session_port=session_cache_adapter
    )

    generate_report_service = GenerateReportService(session_cache_adapter, report_generator_adapter)

    # ── Istanze Controller (Inbound Adapters) ──
    
    query_device_controller = FlaskQueryDeviceController(
        get_device_list_use_case=get_device_list_service,
        get_device_detail_use_case=get_device_detail_service,
        get_compliance_standard_use_case=get_compliance_standard_service,
    )

    write_device_controller = FlaskWriteDeviceController(
        create_device_use_case=create_device_service,
        update_device_use_case=update_device_service,
        delete_device_use_case=delete_device_service,
    )

    import_device_controller = FlaskImportDeviceController(import_device_service=import_device_service)
    export_device_controller = FlaskExportDeviceController(export_device_use_case=export_device_service)

    write_asset_controller = FlaskWriteAssetController(
        create_asset_use_case=create_asset_service,
        update_asset_use_case=update_asset_service,
        delete_asset_use_case=delete_asset_service
    )

    device_evaluation_detail_controller = FlaskDeviceEvaluationDetailController(
        get_device_ev_detail_use_case=get_device_evaluation_detail_service
    )
    
    session_controller = EvaluationSessionController(
        open_use_case=open_session_service,
        close_use_case=close_session_service,
        commit_use_case=commit_session_service
    )

    export_report_controller = FlaskExportReportController(generate_report_use_case=generate_report_service)

    # ── Registrazione Rotte ──
    register_routes(
        app,
        device_controllers=[
            query_device_controller, 
            write_device_controller, 
            import_device_controller,
            export_device_controller  
        ],
        asset_controllers=[ 
            write_asset_controller
        ],
        report_controllers=[export_report_controller],
        evaluation_controllers=[
            device_evaluation_detail_controller, 
            session_controller 
        ] 
    )
    register_error_handlers(app)

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
    @app.route("/health")
    def health_fallback():
        return jsonify({"status": "error", "detail": error}), status

    @app.errorhandler(404)
    def fallback_404(e):
        return jsonify({
            "error": "Servizio non disponibile",
            "detail": f"Database non accessibile: {error}",
        }), status