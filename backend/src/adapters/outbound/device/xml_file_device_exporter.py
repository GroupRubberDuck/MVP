import xml.etree.ElementTree as ET
from src.core.services.device.device_file_command import DeviceFileCommand
from .file_device_exporter import FileDeviceExporter


class XMLFileDeviceExporter(FileDeviceExporter):

    def __init__(self):
        self._root: ET.Element | None = None

    def _prepare_structure(self, device_dto: DeviceFileCommand) -> None:
        # Crea l'elemento root con l'id del device come attributo
        self._root = ET.Element("device", id=device_dto.device.id)

    def _write_data(self, device_dto: DeviceFileCommand) -> None:
        device = device_dto.device

        # Anagrafica device
        ET.SubElement(self._root, "standard_id").text = device.standard_id
        ET.SubElement(self._root, "name").text = device.name
        ET.SubElement(self._root, "os").text = device.os
        ET.SubElement(self._root, "description").text = device.description

        # Assets
        assets_el = ET.SubElement(self._root, "assets")
        for asset in device.assets.values():
            asset_el = ET.SubElement(assets_el, "asset", id=asset.id)

            # Anagrafica asset
            anagraphic_el = ET.SubElement(asset_el, "anagraphic")
            ET.SubElement(anagraphic_el, "name").text = asset.anagraphic.name
            ET.SubElement(anagraphic_el, "asset_type").text = asset.anagraphic.asset_type.value
            ET.SubElement(anagraphic_el, "description").text = asset.anagraphic.description

            # Evidenze
            evidences_el = ET.SubElement(asset_el, "evidences")
            for evidence in asset.proprieties.evidences.values():
                evidence_el = ET.SubElement(
                    evidences_el, "evidence",
                    requirement_id=evidence.requirement_id,
                )
                # Node choices
                choices_el = ET.SubElement(evidence_el, "node_choices")
                for node_id, value in evidence.node_choices.items():
                    ET.SubElement(
                        choices_el, "choice",
                        node_id=node_id,
                        value=str(value).lower(),
                    )
                # Justification
                ET.SubElement(evidence_el, "justification").text = evidence.justification

    def _finalize_output(self) -> bytes:
        ET.indent(self._root)
        return ET.tostring(self._root, encoding="utf-8", xml_declaration=True)