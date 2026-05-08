import io
from datetime import date
from typing import IO
from fpdf import FPDF

from core.domain.evaluation_engine.evaluation_detail import (
    AssetEvaluationDetail,
    DeviceEvaluationDetail,
    RequirementEvaluationDetail,
)
from core.domain.evaluation_standard.evaluation_state import EvaluationState
from core.ports.outbound.report.report_generator_port import ReportGeneratorPort

_STATE_COLORS: dict[EvaluationState, tuple[int, int, int]] = {
    EvaluationState.PASS: (34, 139, 34),
    EvaluationState.FAIL: (178, 34, 34),
    EvaluationState.PENDING: (204, 140, 0),
    EvaluationState.NA: (120, 120, 120),
}


class PdfReportGenerator(ReportGeneratorPort):
    def generate_report(self, detail: DeviceEvaluationDetail) -> IO[bytes]:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        self._format_header(pdf, detail)
        self._print_asset_evaluations(pdf, detail)
        self._format_footer(pdf)
        return io.BytesIO(bytes(pdf.output()))

    def _format_header(self, pdf: FPDF, detail: DeviceEvaluationDetail) -> None:
        pdf.set_font("Helvetica", "B", 20)
        pdf.cell(0, 12, "Compliance Report", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(4)

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Dispositivo", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 7, f"Nome: {detail.name}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, f"Sistema operativo: {detail.operating_system}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, f"Descrizione: {detail.description}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, f"Standard: {detail.standard_id}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        self._print_state_badge(pdf, "Verdetto complessivo", detail.verdict)
        pdf.ln(6)

    def _print_asset_evaluations(self, pdf: FPDF, detail: DeviceEvaluationDetail) -> None:
        for asset in detail.asset_details:
            self._print_asset_section(pdf, asset)

    def _print_asset_section(self, pdf: FPDF, asset: AssetEvaluationDetail) -> None:
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(
            0, 9,
            f"  Asset: {asset.name}  [{asset.asset_type}]",
            new_x="LMARGIN", new_y="NEXT", fill=True,
        )
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, f"  {asset.description}", new_x="LMARGIN", new_y="NEXT")
        self._print_state_badge(pdf, "Verdetto asset", asset.verdict)
        pdf.ln(3)

        for req in asset.requirement_details:
            self._print_requirement_row(pdf, req)
        pdf.ln(4)

    def _print_requirement_row(self, pdf: FPDF, req: RequirementEvaluationDetail) -> None:
        r, g, b = _STATE_COLORS.get(req.state, (0, 0, 0))
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(110, 7, f"  {req.requirement_id} - {req.name}", new_x="RIGHT", new_y="TOP")
        pdf.set_text_color(r, g, b)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, req.state.upper(), new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)

        if req.justification.strip():
            pdf.set_font("Helvetica", "I", 9)
            pdf.cell(0, 6, f"  Giustificazione: {req.justification}", new_x="LMARGIN", new_y="NEXT")

    def _format_footer(self, pdf: FPDF) -> None:
        pdf.set_y(-20)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(
            0, 8,
            f"Generato il {date.today().isoformat()}  -  pagina {pdf.page_no()}",
            new_x="LMARGIN", new_y="NEXT", align="C",
        )
        pdf.set_text_color(0, 0, 0)

    def _print_state_badge(self, pdf: FPDF, label: str, state: EvaluationState) -> None:
        r, g, b = _STATE_COLORS.get(state, (0, 0, 0))
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(50, 7, f"{label}: ", new_x="RIGHT", new_y="TOP")
        pdf.set_text_color(r, g, b)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, state.upper(), new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)