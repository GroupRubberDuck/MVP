import io
import pytest

from adapters.outbound.device.xml_file_device_importer import XMLFileDeviceImporter
from core.ports.outbound.device.exceptions import InvalidFileFormatError


def _to_stream(xml: str) -> io.BytesIO:
    return io.BytesIO(xml.encode())


_VALID_XML = """<device device_id="DEV-001">
    <standard_id>STD-001</standard_id>
    <name>Router</name>
    <os>Linux</os>
    <description>Test</description>
    <assets></assets>
</device>"""

_XML_WITH_ASSET = """<device device_id="DEV-001">
    <standard_id>STD-001</standard_id>
    <name>Router</name>
    <os>Linux</os>
    <description>Test</description>
    <assets>
        <asset id="A1">
            <name>WiFi</name>
            <asset_type>network</asset_type>
            <description>desc</description>
            <evaluations>
                <evaluation requirement_id="REQ-1">
                    <evaluation_map>
                        <choice node_id="N1" value="true"/>
                    </evaluation_map>
                    <justification>ok</justification>
                </evaluation>
            </evaluations>
        </asset>
    </assets>
</device>"""


@pytest.fixture
def importer() -> XMLFileDeviceImporter:
    return XMLFileDeviceImporter()


class TestXMLFileDeviceImporter:

    def test_parses_valid_xml(self, importer):
        device = importer.parse_device_file(_to_stream(_VALID_XML))
        assert device.id == "DEV-001"
        assert device.standard_id == "STD-001"

    def test_parses_asset(self, importer):
        device = importer.parse_device_file(_to_stream(_XML_WITH_ASSET))
        assert "A1" in device.assets

    def test_parses_evaluation_from_xml(self, importer):
        device = importer.parse_device_file(_to_stream(_XML_WITH_ASSET))
        evidence = device.assets["A1"].get_evidence("REQ-1")
        assert evidence is not None
        assert evidence.node_choices["N1"] is True
        assert evidence.justification == "ok"

    def test_raises_invalid_format_on_malformed_xml(self, importer):
        with pytest.raises(InvalidFileFormatError):
            importer.parse_device_file(_to_stream("<device><unclosed>"))