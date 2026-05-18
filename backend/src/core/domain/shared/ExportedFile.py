from dataclasses import dataclass
from typing import IO


@dataclass(frozen=True)
class ExportedFile:
    content: IO[bytes]
    filename: str
    media_type: str
