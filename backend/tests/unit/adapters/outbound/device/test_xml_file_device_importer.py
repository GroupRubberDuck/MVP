import io
import pytest

from adapters.outbound.device.importer.xml_file_device_importer import (
    XMLFileDeviceImporter,
)
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
        """
        Dato un flusso di byte contenente una struttura XML valida che descrive un dispositivo base (Given),
        quando l'importer elabora e deserializza il file (When),
        allora deve istanziare e restituire una corretta entità Device popolando correttamente i campi anagrafici primari (es. ID dispositivo e standard) (Then).
        """
        device = importer.parse_device_file(_to_stream(_VALID_XML))
        assert device.id == "DEV-001"
        assert device.standard_id == "STD-001"

    def test_parses_asset(self, importer):
        """
        Dato un flusso XML che contiene, all'interno del dispositivo, anche la definizione di uno o più asset fisici (Given),
        quando l'importer effettua il parsing del file (When),
        allora il componente Asset deve essere istanziato correttamente e associato al dizionario degli asset del Device (Then).
        """
        device = importer.parse_device_file(_to_stream(_XML_WITH_ASSET))
        assert "A1" in device.assets

    def test_parses_evaluation_from_xml(self, importer):
        """
        Dato un flusso XML in cui un asset possiede un blocco di valutazioni (evidenze, nodi decisionali e giustificazioni) (Given),
        quando il parser naviga l'albero XML per ricostruire il dominio (When),
        allora le evidenze devono essere mappate regolarmente nell'entità AssetEvidence, preservando la mappa delle scelte (node_choices) e le giustificazioni (Then).
        """
        device = importer.parse_device_file(_to_stream(_XML_WITH_ASSET))
        evidence = device.assets["A1"].get_evidence("REQ-1")
        assert evidence is not None
        assert evidence.node_choices["N1"] is True
        assert evidence.justification == "ok"

    def test_raises_invalid_format_on_malformed_xml(self, importer):
        """
        Dato un flusso XML sintatticamente non valido o malformato (es. tag non chiusi correttamente) (Given),
        quando l'importer tenta di effettuare il parsing con la libreria ElementTree (When),
        allora l'errore di parsing deve essere intercettato e ri-lanciato come un'eccezione di dominio InvalidFileFormatError (Then).
        """
        with pytest.raises(InvalidFileFormatError):
            importer.parse_device_file(_to_stream("<device><unclosed>"))
