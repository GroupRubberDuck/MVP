import csv
import io
from core.domain.evaluation_object.device import Device
from adapters.outbound.device.file_device_exporter import FileDeviceExporter


class CSVFileDeviceExporter(FileDeviceExporter):
    def __init__(self):
        self._output: io.StringIO | None = None
        self._writer: csv.writer | None = None

    def _prepare_structure(self, device: Device) -> None:
        self._output = io.StringIO()
        self._writer = csv.writer(self._output)

    def _write_data(self, device: Device) -> None:
        if self._writer is None:
            return

        headers = [
            "device_id", "standard_id", "name", "os", "description",
            "asset_id", "asset_name", "asset_type", "asset_description",
            "requirement_id", "node_id", "node_value", "justification"
        ]
        self._writer.writerow(headers)

        if not device.assets:
            self._writer.writerow([
                device.id, device.standard_id, device.name, device.os, device.description,
                "", "", "", "", "", "", "", ""
            ])
            return

        for asset in device.assets.values():
            if not asset.proprieties.evidences:
                self._writer.writerow([
                    device.id, device.standard_id, device.name, device.os, device.description,
                    asset.id, asset.anagraphic.name, asset.anagraphic.asset_type.value, asset.anagraphic.description,
                    "", "", "", ""
                ])
                continue

            for evidence in asset.proprieties.evidences.values():
                if not evidence.node_choices:
                    self._writer.writerow([
                        device.id, device.standard_id, device.name, device.os, device.description,
                        asset.id, asset.anagraphic.name, asset.anagraphic.asset_type.value, asset.anagraphic.description,
                        evidence.requirement_id, "", "", evidence.justification
                    ])
                    continue

                for node_id, value in evidence.node_choices.items():
                    self._writer.writerow([
                        device.id,
                        device.standard_id,
                        device.name,
                        device.os,
                        device.description,
                        asset.id,
                        asset.anagraphic.name,
                        asset.anagraphic.asset_type.value,
                        asset.anagraphic.description,
                        evidence.requirement_id,
                        node_id,
                        str(value).lower(),
                        evidence.justification
                    ])

    def _finalize_output(self) -> bytes:
        if self._output is None:
            raise RuntimeError("Struttura CSV non inizializzata.")
        return self._output.getvalue().encode("utf-8")