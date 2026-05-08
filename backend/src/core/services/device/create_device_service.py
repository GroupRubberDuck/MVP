from core.ports.inbound.device.exceptions import CreateDeviceFailure
from core.ports.inbound.device.create_device_use_case import CreateDeviceCommand, CreateDeviceUseCase
from core.ports.outbound.device.exceptions import DuplicateDeviceError
from core.ports.outbound.device.register_device_port import RegisterDevicePort  
from core.domain.evaluation_object.device import Device
import uuid


class CreateDeviceService(CreateDeviceUseCase):
    def __init__(self, register_device_port: RegisterDevicePort) -> None:
        self._register_device_port = register_device_port

    def create_device(self, command: CreateDeviceCommand) -> str:
        device_id = str(uuid.uuid4())
        device = Device.create(
            device_id=device_id,
            standard_id=command.standard_id,
            name=command.device_name,
            os=command.device_os,
            description=command.device_description,
        )
        try:
            self._register_device_port.register(device)
        except DuplicateDeviceError as e:
            raise CreateDeviceFailure(
                f"Impossibile creare il dispositivo: {str(e)}"
            ) from e

        return device_id