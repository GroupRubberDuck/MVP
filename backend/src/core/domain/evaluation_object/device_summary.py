from dataclasses import dataclass


@dataclass(frozen=True)
class DeviceSummary:
    device_id: str
    name: str
    os: str
    description: str
    compliance_standard_id: str
