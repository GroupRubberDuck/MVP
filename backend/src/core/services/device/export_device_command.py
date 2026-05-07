from dataclasses import dataclass
from ...domain.evaluation_object.allowed_device_file_extension import AllowedDeviceFileExtension


@dataclass
class ExportDeviceCommand:
    device_id: str
    extension: AllowedDeviceFileExtension