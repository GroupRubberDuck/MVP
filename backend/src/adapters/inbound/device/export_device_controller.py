from flask import Blueprint, request, Response
from core.ports.inbound.device.export_device_use_case import ExportDeviceUseCase
from core.ports.inbound.device.export_device_use_case import ExportDeviceCommand
from core.domain.evaluation_object.allowed_device_file_extension import AllowedDeviceFileExtension
from .download_file_controller import DownloadFileController


class ExportDeviceController:

    def __init__(self, export_uc: ExportDeviceUseCase):
        # Dependency injection nel costruttore
        self._export_uc = export_uc
        self._blueprint = Blueprint("export_device", __name__, url_prefix="/api/devices")
        self._register_routes()

    def _register_routes(self):
        self._blueprint.add_url_rule(
            "/<string:device_id>/export",
            view_func=self.export_device,
            methods=["GET"],
        )

    def export_device(self, device_id: str) -> Response:
        try:
            extension = request.args.get("extension", "json")
            command = ExportDeviceCommand(
                device_id=device_id,
                extension=AllowedDeviceFileExtension(extension),
            )
            file_bytes = self._export_uc.export(command)
            filename = f"device_{device_id}.{extension}"
            return DownloadFileController.build_file_response(file_bytes, filename)
        except ValueError:
            return Response("Formato non supportato", status=400)
        except KeyError:
            return Response("Device non trovato", status=404)

    @property
    def blueprint(self) -> Blueprint:
        return self._blueprint