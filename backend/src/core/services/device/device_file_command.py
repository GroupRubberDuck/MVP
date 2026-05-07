from dataclasses import dataclass
from ...domain.evaluation_object.device import Device

@dataclass
class DeviceFileCommand:
    device: Device