from dataclasses import dataclass
from core.domain.evaluation_object.device import Device
from core.domain.evaluation_standard.compliance_standard import ComplianceStandard

@dataclass
class EvaluationSession:
    session_id: str
    standard: ComplianceStandard
    device: Device

    def insert_justification(
        self,
        asset_id: str,
        requirement_id: str,
        node_id: str,
        justification: str,
    ) -> None:
        asset = self.device.get_asset(asset_id)
        asset.set_justification(requirement_id, justification)