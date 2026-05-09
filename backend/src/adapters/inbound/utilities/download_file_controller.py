from typing import IO
from flask.typing import ResponseReturnValue
from flask import send_file

class DownloadFileController:
    @staticmethod
    def build_file_response(file_bytes: IO[bytes], filename: str) -> ResponseReturnValue:
        return send_file(file_bytes, download_name=filename, as_attachment=True)
