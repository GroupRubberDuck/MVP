from typing import IO

from werkzeug.datastructures import FileStorage

from core.ports.inbound.device.import_device_use_case import AllowedDeviceFileExtension


class UploadFileController:
    @staticmethod
    def get_http_file_extension(filename: str) -> AllowedDeviceFileExtension:
        if "." not in filename:
            raise ValueError(f"Il file '{filename}' non ha un'estensione riconosciuta.")
        raw_ext = filename.rsplit(".", 1)[-1].lower()
        try:
            return AllowedDeviceFileExtension(raw_ext)
        except ValueError:
            allowed = ", ".join(e.value for e in AllowedDeviceFileExtension)
            raise ValueError(
                f"Estensione '.{raw_ext}' non supportata. Estensioni ammesse: {allowed}."
            )

    @staticmethod
    def get_http_file_payload(file: FileStorage) -> IO[bytes]:
        return file.stream
