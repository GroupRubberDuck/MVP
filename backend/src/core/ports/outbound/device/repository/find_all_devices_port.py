from abc import ABC, abstractmethod
from core.domain.evaluation_object.device_summary import DeviceSummary



class FindAllDevicePort(ABC):
    @abstractmethod
    def find_all(self) -> list[DeviceSummary]: ...