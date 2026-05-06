from abc import ABC, abstractmethod
from core.domain.evaluation_standard.compliance_standard import ComplianceStandard

class FindStandardPort(ABC):
    @abstractmethod
    def find_standard(self, standard_id: str)-> ComplianceStandard:
        pass