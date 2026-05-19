from pydantic import BaseModel
from abc import ABC, abstractmethod
from core.domain.evaluation_standard.compliance_standard import ComplianceStandard


class GetComplianceStandardCommand(BaseModel):
    standard_id: str


class GetComplianceStandardUseCase(ABC):
    @abstractmethod
    def get_compliance_standard(
        self, command: GetComplianceStandardCommand
    ) -> ComplianceStandard:
        """Restituisce il compliance standard corrispondente all'ID fornito.

        Raises:
            StandardNotFoundFailure: se lo standard non esiste.
        """
        ...
