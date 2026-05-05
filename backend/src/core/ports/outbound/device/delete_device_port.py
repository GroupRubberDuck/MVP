from abc import ABC, abstractmethod


class DeleteDevicePort(ABC):
    @abstractmethod
    def delete(self, device_id: str) -> None: ...