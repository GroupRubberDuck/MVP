from typing import IO
from dataclasses import dataclass

@dataclass(frozen=True)
class ExportedFile:
    content: IO[bytes]
    filename: str
    media_type: str