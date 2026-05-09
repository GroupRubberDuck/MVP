from core.ports.inbound.report.generate_report_use_case import GenerateReportUseCase, GenerateReportCommand
from core.ports.inbound.report.exceptions import ExportReportFailure
from core.ports.outbound.evaluation.get_evaluation_session_port import GetEvaluationSessionPort
from core.ports.outbound.evaluation.exceptions import EvaluationSessionNotFoundError
from core.ports.outbound.report.report_generator_port import ReportGeneratorPort
from core.domain.evaluation_engine.evaluation_engine import EvaluationEngine
from core.domain.evaluation_engine.evaluation_detail import (
    DeviceEvaluationDetail, AssetEvaluationDetail, RequirementEvaluationDetail,
)
from core.domain.evaluation_engine.evaluation_result import (
    DeviceEvaluationResult, AssetEvaluationResult, RequirementEvaluationResult,
)
from core.domain.evaluation_standard.compliance_standard import ComplianceStandard
from core.domain.evaluation_standard.requirement import Requirement
from core.domain.shared.exceptions import DomainError
from core.domain.ExportedFile import ExportedFile

from core.domain.evaluation_object.device import Device

class GenerateReportService(GenerateReportUseCase):
    def __init__(
        self,
        get_evaluation_session_port: GetEvaluationSessionPort,
        report_generator_port: ReportGeneratorPort,
        evaluation_engine: EvaluationEngine = EvaluationEngine(),
    ) -> None:
        self._get_evaluation_session_port = get_evaluation_session_port
        self._report_generator = report_generator_port
        self._evaluation_engine = evaluation_engine

    def export_report(self, command: GenerateReportCommand) -> ExportedFile:
        try:
            session = self._get_evaluation_session_port.get_evaluation_session(command.session_id)
        except EvaluationSessionNotFoundError as e:
            raise ExportReportFailure(
                f"Sessione '{command.session_id}' non trovata."
            ) from e
        try:
            device_result = self._evaluation_engine.evaluate(
                session.device, session.standard
            )
        except DomainError as e:
            raise ExportReportFailure(str(e)) from e

        detail = self._build_device_detail(device_result, session.device, session.standard) 
        return ExportedFile(
            self._report_generator.generate_report(detail),
            media_type=command.report_format.media_type,
            filename=f"{session.device.name}_report.{command.report_format.value}"
            )

    def _build_device_detail(
        self, result: DeviceEvaluationResult, device:Device, standard: ComplianceStandard
    ) -> DeviceEvaluationDetail:
        asset_details = tuple(
            self._build_asset_detail(ar, device, standard )
            for ar in result.asset_results
        )
        return DeviceEvaluationDetail(
            device_id=device.id,
            name=device.name,
            operating_system=device.os,
            description=device.description,
            standard_id=standard.id,
            asset_details=asset_details,
            verdict=result.verdict,
        )

    def _build_asset_detail(
        self, result: AssetEvaluationResult, device:Device, standard: ComplianceStandard
    ) -> AssetEvaluationDetail:
        asset = device.get_asset(result.asset_id)
        requirement_details = tuple(
            self._build_requirement_detail(rr, standard.get_requirement(rr.requirement_id))
            for rr in result.requirement_results
        )
        return AssetEvaluationDetail(
            asset_id=asset.id,
            name=asset.anagraphic.name,
            asset_type=asset.anagraphic.asset_type,
            description=asset.anagraphic.description,
            requirement_details=requirement_details,
            verdict=result.verdict,
        )

    def _build_requirement_detail(
        self, result: RequirementEvaluationResult, req: Requirement
    ) -> RequirementEvaluationDetail:
        if req.decision_tree is None:
            raise ExportReportFailure(
                f"Il requisito '{req.requirement_id}' non ha un albero decisionale."
            )
        return RequirementEvaluationDetail(
            requirement_id=result.requirement_id,
            name=req.name,
            description=req.description,
            target=req.target_description,
            justification=result.justification,
            node_choices=result.node_choices,
            nodes=req.decision_tree.nodes,
            state=result.state,
            dependencies=result.dependencies,
        )