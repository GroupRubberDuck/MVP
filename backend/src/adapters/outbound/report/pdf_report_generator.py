import io
from datetime import date
from typing import IO
from fpdf import FPDF
from pathlib import Path 

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
    def generate_report(self, device_evaluation: DeviceEvaluationDetail) -> IO[bytes]:
        pdf = FPDF()
        current_dir = Path(__file__).parent
        fonts_dir = current_dir / "fonts"


        pdf.add_font("Roboto", "", str(fonts_dir / "Roboto-Regular.ttf"))
        pdf.add_font("Roboto", "B", str(fonts_dir / "Roboto-Bold.ttf"))
        pdf.add_font("Roboto", "I", str(fonts_dir / "Roboto-Italic.ttf"))

        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        self._format_header(pdf, device_evaluation)
        self._print_asset_evaluations(pdf, device_evaluation)
        self._format_footer(pdf)
        
        return io.BytesIO(bytes(pdf.output()))

    def _format_header(self, pdf: FPDF, device_evaluation: DeviceEvaluationDetail) -> None:
        # Titolo Principale
        pdf.set_font("Roboto", "B", 22)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(0, 15, "Compliance Report", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(5)

        # Sezione Dispositivo
        pdf.set_font("Roboto", "B", 13)
        pdf.cell(0, 8, "INFORMAZIONI DISPOSITIVO", new_x="LMARGIN", new_y="NEXT")
        pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
        pdf.ln(2)

        pdf.set_font("Roboto", "", 11)
        pdf.multi_cell(0, 7, f"Nome: {device_evaluation.name}", new_x="LMARGIN", new_y="NEXT")
        pdf.multi_cell(0, 7, f"Sistema operativo: {device_evaluation.operating_system}", new_x="LMARGIN", new_y="NEXT")
        pdf.multi_cell(0, 7, f"Descrizione: {device_evaluation.description or 'N/A'}", new_x="LMARGIN", new_y="NEXT")
        pdf.multi_cell(0, 7, f"Standard applicato: {device_evaluation.standard_id}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        self._print_state_badge(pdf, "Verdetto complessivo", device_evaluation.verdict)
        pdf.ln(10)

    def _print_asset_evaluations(self, pdf: FPDF, detail: DeviceEvaluationDetail) -> None:
        for asset in detail.asset_details:
            # Controllo salto pagina per gli header degli asset
            if pdf.get_y() > 250:
                pdf.add_page()
            self._print_asset_section(pdf, asset)

    def _print_asset_section(self, pdf: FPDF, asset: AssetEvaluationDetail) -> None:
        # Header dell'Asset (Barra grigia)
        pdf.set_font("Roboto", "B", 12)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 10, f"  ASSET: {asset.name.upper()}  [{asset.asset_type.upper()}]", 
                 new_x="LMARGIN", new_y="NEXT", fill=True)
        
        pdf.set_font("Roboto", "I", 10)
        pdf.set_text_color(80, 80, 80)
        pdf.multi_cell(0, 7, f"  Descrizione: {asset.description or 'Nessuna descrizione'}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        
        self._print_state_badge(pdf, "  Stato Asset", asset.verdict)
        pdf.ln(4)

        # Tabella Requisiti
        for req in asset.requirement_details:
            self._print_requirement_row(pdf, req)
        pdf.ln(6)

    def _print_requirement_row(self, pdf: FPDF, req: RequirementEvaluationDetail) -> None:
        # CONTROLLO ANTI-SBALLAMENTO PAGINA
        if pdf.get_y() > 260:
            pdf.add_page()

        r, g, b = _STATE_COLORS.get(req.state, (0, 0, 0))
        
        
        start_y = pdf.get_y()
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Roboto", "B", 10)
        pdf.multi_cell(155, 7, f"  {req.requirement_id} - {req.name}", new_x="LMARGIN", new_y="NEXT")
        
        end_y = pdf.get_y()

        pdf.set_y(start_y)
        pdf.set_font("Roboto", "B", 9)
        pdf.set_text_color(r, g, b)
        pdf.cell(0, 7, req.state.name.upper(), align="R", new_x="LMARGIN", new_y="NEXT")
        

        pdf.set_y(max(end_y, pdf.get_y()))

        # 5. Giustificazione (se presente)
        if req.justification and req.justification.strip():
            pdf.set_font("Roboto", "I", 9)
            pdf.set_text_color(100, 100, 100)
            # Rientro per la giustificazione
            pdf.set_x(pdf.get_x() + 5)
            pdf.multi_cell(150, 5, f"Nota: {req.justification}", new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)
            
        
        pdf.ln(2)

    def _format_footer(self, pdf: FPDF) -> None:
        pdf.set_y(-20)
        pdf.set_font("Roboto", "I", 8)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 10, f"Generato il {date.today().strftime('%d/%m/%Y')} - Pagina {pdf.page_no()}", 
                 align="C", new_x="LMARGIN", new_y="NEXT")

    def _print_state_badge(self, pdf: FPDF, label: str, state: EvaluationState) -> None:
        r, g, b = _STATE_COLORS.get(state, (0, 0, 0))
        pdf.set_font("Roboto", "", 10)
        pdf.cell(45, 8, f"{label}: ", new_x="RIGHT", new_y="TOP")
        
        pdf.set_font("Roboto", "B", 10)
        pdf.set_text_color(r, g, b)
        state_text = state.name if hasattr(state, 'name') else str(state)
        pdf.cell(0, 8, state_text.upper(), new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)