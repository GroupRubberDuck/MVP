import csv
import io
from src.core.services.device.device_file_command import DeviceFileCommand
from .file_device_exporter import FileDeviceExporter


class CSVFileDeviceExporter(FileDeviceExporter):

    def __init__(self):
        self._output: io.StringIO | None = None
        self._writer: csv.writer | None = None

    def _prepare_structure(self, device_dto: DeviceFileCommand) -> None:
        # Inizializza il buffer di testo in memoria
        self._output = io.StringIO()
        self._writer = csv.writer(self._output)

    def _write_data(self, device_dto: DeviceFileCommand) -> None:
        device = device_dto.device

        #  sezione DEVICE 
        self._writer.writerow(["# DEVICE"])
        self._writer.writerow(["id", "standard_id", "name", "os", "description"])
        self._writer.writerow([
            device.id,
            device.standard_id,
            device.name,
            device.os,
            device.description,
        ])

        # riga vuota come separatore
        self._writer.writerow([])

        # sezione ASSETS 
        self._writer.writerow(["# ASSETS"])
        self._writer.writerow(["asset_id", "name", "asset_type", "description"])
        for asset in device.assets.values():
            self._writer.writerow([
                asset.id,
                asset.anagraphic.name,
                asset.anagraphic.asset_type.value,
                asset.anagraphic.description,
            ])

        # riga vuota come separatore
        self._writer.writerow([])

        #sezione EVIDENCES 
        self._writer.writerow(["# EVIDENCES"])
        self._writer.writerow([
            "asset_id", "requirement_id", "node_id", "value", "justification"
        ])
        for asset in device.assets.values():
            for evidence in asset.proprieties.evidences.values():
                if evidence.node_choices:
                    # una riga per ogni node_choice
                    for node_id, value in evidence.node_choices.items():
                        self._writer.writerow([
                            asset.id,
                            evidence.requirement_id,
                            node_id,
                            str(value).lower(),
                            evidence.justification,
                        ])
                else:
                    # evidence senza node_choices — solo justification
                    self._writer.writerow([
                        asset.id,
                        evidence.requirement_id,
                        "",
                        "",
                        evidence.justification,
                    ])

    def _finalize_output(self) -> bytes:
        # Converte il buffer di testo in bytes UTF-8
        return self._output.getvalue().encode("utf-8")