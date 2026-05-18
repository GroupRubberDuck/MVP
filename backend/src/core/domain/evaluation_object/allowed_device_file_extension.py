from enum import StrEnum


class AllowedDeviceFileExtension(StrEnum):
    XML = "xml"
    JSON = "json"
    CSV = "csv"

    @property
    def media_type(self) -> str:
        mapping = {
            "csv": "text/csv",
            "xml": "application/xml",
            "json": "application/json",
        }
        return mapping[self.value]
