from core.ports.inbound.evaluation.evaluation_session.open_evaluation_session_use_case import (
        OpenEvaluationSessionUseCase,
        OpenEvaluationSessionCommand
)



from .session_coordinator import SessionCoordinator


from core.ports.outbound.evaluation.evaluation_session.create_evaluation_session_port import CreateEvaluationSessionPort
from core.ports.outbound.device.repository.find_device_port import FindDevicePort
from core.ports.outbound.device.exceptions import DeviceNotFoundError 
from core.ports.outbound.compliance_standard.find_standard_port import FindStandardPort
from core.ports.outbound.compliance_standard.exceptions import StandardNotFoundError
# eccezioni
from core.ports.inbound.evaluation.exceptions import OpenEvaluationSessionFailure

from core.ports.outbound.evaluation.exceptions import EvaluationSessionOpenError

class OpenEvaluationSessionService(OpenEvaluationSessionUseCase):
        def __init__(
                self, 
                session_coordinator: SessionCoordinator, 
                create_session_port: CreateEvaluationSessionPort,
                find_device_port: FindDevicePort,
                find_standard_port: FindStandardPort
        ) -> None:
                self._session_coordinator = session_coordinator
                self._create_session_port = create_session_port
                self._find_device_port = find_device_port
                self._find_standard_port = find_standard_port

        def open_evaluation_session(self, command: OpenEvaluationSessionCommand) -> str:
                if not self._session_coordinator.can_open_session():
                        raise OpenEvaluationSessionFailure("Non è possibile aprire una nuova sessione di valutazione. Esiste già una sessione attiva.")
                
                try:
                        device=self._find_device_port.find_by_id(command.device_id)
                except DeviceNotFoundError :
                        raise OpenEvaluationSessionFailure(
                                f"impossibile aprire la session, il dispositivo {command.device_id} non trovato"
                                )
                try:
                        standard=self._find_standard_port.find_standard(device.standard_id)
                except StandardNotFoundError :
                        raise OpenEvaluationSessionFailure(
                                f"impossibile aprire la session, lo standard {device.standard_id} non trovato"
                                )
                try:
                        session = self._create_session_port.create_evaluation_session(standard=standard,device=device)
                        return session.session_id
                except EvaluationSessionOpenError as e:
                        raise OpenEvaluationSessionFailure(f"Errore durante l'apertura della sessione di valutazione: {str(e)}") from e