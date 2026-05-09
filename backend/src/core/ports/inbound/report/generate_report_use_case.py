from abc import ABC, abstractmethod
from enum import StrEnum
from pydantic import BaseModel
from core.domain.ExportedFile import ExportedFile

class ReportFormat(StrEnum):
    PDF = "pdf"
    @property
    def media_type(self) -> str:
        mapping = {
            "pdf": "application/pdf",
        }
        return mapping[self.value]

class GenerateReportCommand(BaseModel):
    session_id: str
    device_id: str
    report_format: ReportFormat


class GenerateReportUseCase(ABC):
    @abstractmethod
    def export_report(self, command: GenerateReportCommand) -> ExportedFile: ...