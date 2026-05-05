from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import BinaryIO


class AllowedDeviceFileExtension(StrEnum):
    CSV = "csv"
    XML = "xml"
    JSON = "json"


@dataclass(frozen=True)
class ImportDeviceCommand:
    device_file_content: BinaryIO
    extension: AllowedDeviceFileExtension


class ImportDeviceUseCase(ABC):
    @abstractmethod
    def import_device(self, command: ImportDeviceCommand) -> None: ...