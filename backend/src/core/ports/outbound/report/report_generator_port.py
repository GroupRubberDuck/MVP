from abc import ABC, abstractmethod
from core.domain.evaluation_engine.evaluation_detail import DeviceEvaluationDetail


class ReportGeneratorPort(ABC):
    @abstractmethod
    def generate_report(device_evaluation: DeviceEvaluationDetail) -> None: ...