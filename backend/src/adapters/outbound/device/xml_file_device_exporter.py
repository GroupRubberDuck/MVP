import xml.etree.ElementTree as ET
from core.domain.evaluation_object.device import Device
from adapters.outbound.device.file_device_exporter import FileDeviceExporter


class XMLFileDeviceExporter(FileDeviceExporter):
    def __init__(self):
        self._root: ET.Element | None = None

    def _prepare_structure(self, device: Device) -> None:
        self._root = ET.Element("device", device_id=device.id)

    def _write_data(self, device: Device) -> None:
        if self._root is None:
            return

        # Dati del dispositivo
        ET.SubElement(self._root, "standard_id").text = device.standard_id
        ET.SubElement(self._root, "name").text = device.name
        ET.SubElement(self._root, "os").text = device.os
        ET.SubElement(self._root, "description").text = device.description

        # Assets
        assets_el = ET.SubElement(self._root, "assets")
        for asset in device.assets.values():
            asset_el = ET.SubElement(assets_el, "asset", id=asset.id)

            ET.SubElement(asset_el, "name").text = asset.anagraphic.name
            ET.SubElement(asset_el, "asset_type").text = asset.anagraphic.asset_type.value
            ET.SubElement(asset_el, "description").text = asset.anagraphic.description
            evaluations_el = ET.SubElement(asset_el, "evaluations")
            for evidence in asset.proprieties.evidences.values():
                evaluation_el = ET.SubElement(
                    evaluations_el,
                    "evaluation",
                    requirement_id=evidence.requirement_id,
                )
            
                evaluation_map_el = ET.SubElement(evaluation_el, "evaluation_map")
                for node_id, value in evidence.node_choices.items():
                    ET.SubElement(
                        evaluation_map_el,
                        "choice",
                        node_id=node_id,
                        value=str(value).lower(),
                    )
                
                # Justification
                ET.SubElement(evaluation_el, "justification").text = evidence.justification

    def _finalize_output(self) -> bytes:
        if self._root is None:
            raise RuntimeError("Struttura XML non inizializzata.")
            
        ET.indent(self._root)
        return ET.tostring(self._root, encoding="utf-8", xml_declaration=True)