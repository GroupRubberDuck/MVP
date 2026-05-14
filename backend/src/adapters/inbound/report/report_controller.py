from flask import Blueprint, send_file, jsonify
from flask.typing import ResponseReturnValue

from adapters.inbound.flask_controller_interface import FlaskController
from core.ports.inbound.report.generate_report_use_case import (
    GenerateReportUseCase,
    GenerateReportCommand,
    ReportFormat
)
from core.ports.inbound.report.exceptions import ExportReportFailure


class FlaskExportReportController(FlaskController):

    def __init__(self, generate_report_use_case: GenerateReportUseCase) -> None:
        self._generate_report_use_case = generate_report_use_case

    def register_routes(self, blueprint: Blueprint) -> None:

        @blueprint.route(
            "/sessions/<session_id>/devices/<device_id>/report/<fmt>",
            methods=["GET"],
        )
        def export_report(session_id: str, device_id: str, fmt: str) -> ResponseReturnValue:
            try:
                report_format = ReportFormat(fmt)
            except ValueError:
                return jsonify({"error": f"Formato non supportato: '{fmt}'."}), 400
        
            command = GenerateReportCommand(
                report_format=report_format,
                session_id=session_id,
                device_id=device_id,
            )
        
            try:
                exported = self._generate_report_use_case.export_report(command)
            except ExportReportFailure as e:
                return jsonify({"error": str(e)}), 422
        
            return send_file(
                exported.content,
                mimetype=exported.media_type,
                as_attachment=True,
                download_name=exported.filename,
            )