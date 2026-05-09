from abc import ABC, abstractmethod
from pydantic import BaseModel
from core.domain.evaluation_engine.evaluation_detail import DeviceEvaluationDetail 

class GetDeviceEvaluationDetailCommand(BaseModel):
    session_id: str
    device_id: str

class GetDeviceEvaluationDetailUseCase(ABC):    
    @abstractmethod
    def get_device_evaluation_detail(
        self, command: GetDeviceEvaluationDetailCommand
    ) -> DeviceEvaluationDetail:
        pass