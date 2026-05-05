from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class DeviceSummary:
    device_id: str
    name: str
    os: str
    description: str
    compliance_standard_id: str


class FindAllDevicePort(ABC):
    @abstractmethod
    def find_all(self) -> list[DeviceSummary]: ...