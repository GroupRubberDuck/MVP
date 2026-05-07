from flask import Response


class DownloadFileController:

    @staticmethod
    def build_file_response(file_bytes: bytes, filename: str) -> Response:
        # Costruisce la risposta HTTP con il file da scaricare
        return Response(
            file_bytes,
            mimetype="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )