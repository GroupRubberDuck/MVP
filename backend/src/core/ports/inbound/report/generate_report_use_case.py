from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import IO


class ReportFormat(StrEnum):
    PDF = "pdf"


@dataclass(frozen=True)
class GenerateReportCommand:
    session_id: str
    report_format: ReportFormat


class GenerateReportUseCase(ABC):
    @abstractmethod
    def export_report(self, command: GenerateReportCommand) -> IO[bytes]: ...