from core.ports.inbound.report.generate_report_use_case import GenerateReportUseCase, GenerateReportCommand
from core.ports.inbound.report.exceptions import ExportReportFailure
from adapters.inbound.utilities.download_file_controller import DownloadFileController
from adapters.inbound.flask_controller_interface import FlaskController
from flask import Blueprint, render_template
from flask.typing import ResponseReturnValue

class FlaskExportReportController(FlaskController):
    def __init__(
        self,
        generate_report_use_case: GenerateReportUseCase
    ) -> None:
        self._generate_report_use_case = generate_report_use_case

    def register_routes(self, blueprint: Blueprint) -> None:
        @blueprint.route("/report/<fmt>", methods=["GET"])
        def export_report(fmt) -> ResponseReturnValue:
            command = GenerateReportCommand(format=fmt)
            try:
                report = self._generate_report_use_case.export_report(command)
            except ExportReportFailure as e:
                return render_template("error.html", message=str(e)), 500
                
            return DownloadFileController.build_file_response(report, f'report.{fmt}'), 200