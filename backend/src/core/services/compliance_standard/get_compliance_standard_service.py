from core.ports.inbound.compliance_standard.get_compliance_standard_use_case import GetComplianceStandardCommand, GetComplianceStandardUseCase
from core.ports.inbound.compliance_standard.exceptions import StandardNotFoundFailure


from core.ports.outbound.compliance_standard.find_standard_port import FindStandardPort
from core.ports.outbound.compliance_standard.exceptions import StandardNotFoundError


from core.domain.evaluation_standard.compliance_standard import ComplianceStandard

class GetComplianceStandardService(GetComplianceStandardUseCase):
    def __init__(self, find_standard_port: FindStandardPort) -> None:
        self._find_standard_port = find_standard_port

    def get_compliance_standard(self, command: GetComplianceStandardCommand) -> ComplianceStandard:
        try:
                return self._find_standard_port.find_standard(command.standard_id)
        except StandardNotFoundError as e:
            raise StandardNotFoundFailure(f"Compliance standard not found: {command.standard_id}") from e