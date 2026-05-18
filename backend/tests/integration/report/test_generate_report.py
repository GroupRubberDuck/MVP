import pytest
from core.ports.inbound.evaluation.evaluation_session.open_evaluation_session_use_case import (
    OpenEvaluationSessionCommand,
)
from core.ports.inbound.evaluation.evaluate_decision_node_use_case import (
    EvaluateDecisionNodeCommand,
)
from core.ports.inbound.report.generate_report_use_case import (
    GenerateReportCommand,
    ReportFormat,
)
from core.ports.inbound.report.exceptions import ExportReportFailure


class TestGenerazioneReportPdf:
    def test_report(self, evaluation_services, device_adapter, device_with_asset):
        device_adapter.register(device_with_asset)
        session_id = evaluation_services["open"].open_evaluation_session(
            OpenEvaluationSessionCommand(device_id=device_with_asset.id)
        )
        exported = evaluation_services["report"].export_report(
            GenerateReportCommand(
                session_id=session_id,
                device_id=device_with_asset.id,
                report_format=ReportFormat.PDF,
            )
        )
        content = exported.content.read()
        assert len(content) > 0, "Il PDF generato è vuoto"
        assert content[:4] == b"%PDF", "Il file non inizia con la firma PDF"

    def test_report_con_valutazioni_compilate(
        self, evaluation_services, device_adapter, device_with_asset
    ):
        device_adapter.register(device_with_asset)
        session_id = evaluation_services["open"].open_evaluation_session(
            OpenEvaluationSessionCommand(device_id=device_with_asset.id)
        )
        evaluation_services["evaluate_node"].evaluate_node(
            EvaluateDecisionNodeCommand(
                session_id=session_id,
                device_id=device_with_asset.id,
                asset_id="asset-001",
                requirement_id="REQ-002",
                node_id="N1",
                answer=True,
            )
        )
        exported = evaluation_services["report"].export_report(
            GenerateReportCommand(
                session_id=session_id,
                device_id=device_with_asset.id,
                report_format=ReportFormat.PDF,
            )
        )
        content = exported.content.read()
        assert len(content) > 0
        assert content[:4] == b"%PDF"

    def test_report_sessione_inesistente(self, evaluation_services, device_with_asset):
        with pytest.raises(ExportReportFailure):
            evaluation_services["report"].export_report(
                GenerateReportCommand(
                    session_id="sessione-inesistente",
                    device_id=device_with_asset.id,
                    report_format=ReportFormat.PDF,
                )
            )
