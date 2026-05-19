from abc import ABC, abstractmethod
from core.domain.evaluation_object.device_summary import DeviceSummary


class GetDeviceListUseCase(ABC):
    @abstractmethod
    def get_device_list(self) -> list[DeviceSummary]: 
        """Restituisce la lista di tutti i dispositivi registrati."""
        ...