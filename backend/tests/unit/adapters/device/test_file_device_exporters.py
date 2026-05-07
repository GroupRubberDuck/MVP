import pytest
import xml.etree.ElementTree as ET
import json
import csv
import io
from src.core.domain.evaluation_object.device import Device
from src.core.domain.evaluation_object.asset.asset import Asset
from src.core.domain.evaluation_object.asset.asset_anagraphic import AssetAnagraphic
from src.core.domain.evaluation_object.asset.asset_proprieties import AssetProprieties
from src.core.domain.evaluation_object.asset.asset_evidence import AssetEvidence
from src.core.domain.evaluation_object.asset.asset_type import AssetType
from src.core.domain.evaluation_object.allowed_device_file_extension import AllowedDeviceFileExtension
from src.core.services.device.device_file_command import DeviceFileCommand
from src.adapters.outbound.device.xml_file_device_exporter import XMLFileDeviceExporter
from src.adapters.outbound.device.json_file_device_exporter import JSONFileDeviceExporter
from src.adapters.outbound.device.csv_file_device_exporter import CSVFileDeviceExporter
from src.adapters.outbound.device.concrete_file_device_exporter_factory import ConcreteFileDeviceExporterFactory
from types import MappingProxyType


# fixtures 

@pytest.fixture
def evidence():
    return AssetEvidence(
        requirement_id="req-1",
        node_choices=MappingProxyType({"node-1": True, "node-2": False}),
        justification="Motivazione test",
    )

@pytest.fixture
def asset(evidence):
    proprieties = AssetProprieties({"req-1": evidence})
    return Asset(
        id="asset-1",
        anagraphic=AssetAnagraphic(
            name="Router",
            asset_type=AssetType.NETWORK,
            description="Router di test",
        ),
        proprieties=proprieties,
    )

@pytest.fixture
def device(asset):
    d = Device.create(
        device_id="device-1",
        standard_id="standard-1",
        name="Test Device",
        os="Linux",
        description="Device di test",
    )
    d.add_asset(asset)
    return d

@pytest.fixture
def command(device):
    return DeviceFileCommand(device=device)


#  XML 

class TestXMLFileDeviceExporter:

    def test_output_e_bytes(self, command):
        # Il risultato deve essere bytes
        result = XMLFileDeviceExporter().generate_device_file(command)
        assert isinstance(result, bytes)

    def test_contiene_id_device(self, command):
        # L'elemento root deve avere l'id del device come attributo
        result = XMLFileDeviceExporter().generate_device_file(command)
        root = ET.fromstring(result)
        assert root.attrib["id"] == "device-1"

    def test_contiene_nome_device(self, command):
        # Il campo name del device deve essere presente
        result = XMLFileDeviceExporter().generate_device_file(command)
        root = ET.fromstring(result)
        assert root.find("name").text == "Test Device"

    def test_contiene_asset(self, command):
        # Deve esserci esattamente 1 asset
        result = XMLFileDeviceExporter().generate_device_file(command)
        root = ET.fromstring(result)
        assets = root.findall("assets/asset")
        assert len(assets) == 1

    def test_asset_ha_id_corretto(self, command):
        # L'asset deve avere l'id corretto
        result = XMLFileDeviceExporter().generate_device_file(command)
        root = ET.fromstring(result)
        asset_el = root.find("assets/asset")
        assert asset_el.attrib["id"] == "asset-1"

    def test_asset_ha_tipo_corretto(self, command):
        # Il tipo dell'asset deve essere serializzato come stringa
        result = XMLFileDeviceExporter().generate_device_file(command)
        root = ET.fromstring(result)
        asset_type = root.find("assets/asset/anagraphic/asset_type").text
        assert asset_type == "network"

    def test_contiene_evidenza(self, command):
        # Deve esserci esattamente 1 evidenza
        result = XMLFileDeviceExporter().generate_device_file(command)
        root = ET.fromstring(result)
        evidences = root.findall("assets/asset/evidences/evidence")
        assert len(evidences) == 1

    def test_evidenza_ha_node_choices(self, command):
        # Le node_choices devono essere serializzate correttamente
        result = XMLFileDeviceExporter().generate_device_file(command)
        root = ET.fromstring(result)
        choices = root.findall("assets/asset/evidences/evidence/node_choices/choice")
        assert len(choices) == 2

    def test_evidenza_ha_justification(self, command):
        # La justification deve essere presente
        result = XMLFileDeviceExporter().generate_device_file(command)
        root = ET.fromstring(result)
        justification = root.find(
            "assets/asset/evidences/evidence/justification"
        ).text
        assert justification == "Motivazione test"


# JSON 

class TestJSONFileDeviceExporter:

    def test_output_e_bytes(self, command):
        # Il risultato deve essere bytes
        result = JSONFileDeviceExporter().generate_device_file(command)
        assert isinstance(result, bytes)

    def test_json_valido(self, command):
        # Il risultato deve essere JSON valido
        result = JSONFileDeviceExporter().generate_device_file(command)
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_contiene_id_device(self, command):
        # Il campo id deve corrispondere a quello del device
        result = JSONFileDeviceExporter().generate_device_file(command)
        data = json.loads(result)
        assert data["id"] == "device-1"

    def test_contiene_nome_device(self, command):
        # Il campo name deve essere presente
        result = JSONFileDeviceExporter().generate_device_file(command)
        data = json.loads(result)
        assert data["name"] == "Test Device"

    def test_contiene_asset(self, command):
        # Deve esserci esattamente 1 asset
        result = JSONFileDeviceExporter().generate_device_file(command)
        data = json.loads(result)
        assert len(data["assets"]) == 1

    def test_asset_ha_tipo_corretto(self, command):
        # Il tipo dell'asset deve essere serializzato come stringa
        result = JSONFileDeviceExporter().generate_device_file(command)
        data = json.loads(result)
        assert data["assets"][0]["anagraphic"]["asset_type"] == "network"

    def test_contiene_evidenza(self, command):
        # Deve esserci esattamente 1 evidenza
        result = JSONFileDeviceExporter().generate_device_file(command)
        data = json.loads(result)
        assert len(data["assets"][0]["evidences"]) == 1

    def test_evidenza_ha_node_choices(self, command):
        # Le node_choices devono essere serializzate come dizionario
        result = JSONFileDeviceExporter().generate_device_file(command)
        data = json.loads(result)
        choices = data["assets"][0]["evidences"][0]["node_choices"]
        assert choices["node-1"] is True
        assert choices["node-2"] is False


#  CSV 

class TestCSVFileDeviceExporter:

    def _parse_csv(self, result: bytes) -> dict:
        # Helper che divide il CSV nelle tre sezioni
        content = result.decode("utf-8")
        sections = {"DEVICE": [], "ASSETS": [], "EVIDENCES": []}
        current = None
        reader = csv.reader(io.StringIO(content))
        for row in reader:
            if not row:
                continue
            if row[0] == "# DEVICE":
                current = "DEVICE"
            elif row[0] == "# ASSETS":
                current = "ASSETS"
            elif row[0] == "# EVIDENCES":
                current = "EVIDENCES"
            elif current:
                sections[current].append(row)
        return sections

    def test_output_e_bytes(self, command):
        # Il risultato deve essere bytes
        result = CSVFileDeviceExporter().generate_device_file(command)
        assert isinstance(result, bytes)

    def test_contiene_sezione_device(self, command):
        # La sezione DEVICE deve avere header + 1 riga dati
        result = CSVFileDeviceExporter().generate_device_file(command)
        sections = self._parse_csv(result)
        assert len(sections["DEVICE"]) == 2  # header + 1 riga

    def test_device_ha_id_corretto(self, command):
        # La riga dati del device deve avere l'id corretto
        result = CSVFileDeviceExporter().generate_device_file(command)
        sections = self._parse_csv(result)
        assert sections["DEVICE"][1][0] == "device-1"

    def test_contiene_sezione_assets(self, command):
        # La sezione ASSETS deve avere header + 1 riga dati
        result = CSVFileDeviceExporter().generate_device_file(command)
        sections = self._parse_csv(result)
        assert len(sections["ASSETS"]) == 2  # header + 1 riga

    def test_asset_ha_tipo_corretto(self, command):
        # Il tipo dell'asset deve essere serializzato come stringa
        result = CSVFileDeviceExporter().generate_device_file(command)
        sections = self._parse_csv(result)
        assert sections["ASSETS"][1][2] == "network"

    def test_contiene_sezione_evidences(self, command):
        # La sezione EVIDENCES deve avere header + 2 righe (2 node_choices)
        result = CSVFileDeviceExporter().generate_device_file(command)
        sections = self._parse_csv(result)
        assert len(sections["EVIDENCES"]) == 3  # header + 2 righe

    def test_evidenza_ha_node_id_corretto(self, command):
        # Il node_id deve essere presente nelle righe delle evidenze
        result = CSVFileDeviceExporter().generate_device_file(command)
        sections = self._parse_csv(result)
        node_ids = [row[2] for row in sections["EVIDENCES"][1:]]
        assert "node-1" in node_ids
        assert "node-2" in node_ids

    def test_evidenza_ha_justification_corretta(self, command):
    # La justification deve essere presente nelle righe delle evidenze
        result = CSVFileDeviceExporter().generate_device_file(command)
        sections = self._parse_csv(result)
        justifications = [row[4] for row in sections["EVIDENCES"][1:]]
        assert "Motivazione test" in justifications


# Factory 

class TestConcreteFileDeviceExporterFactory:

    def test_restituisce_xml_exporter(self):
        # La factory deve restituire XMLFileDeviceExporter per XML
        factory = ConcreteFileDeviceExporterFactory()
        exporter = factory.get_file_device_exporter(AllowedDeviceFileExtension.XML)
        assert isinstance(exporter, XMLFileDeviceExporter)

    def test_restituisce_json_exporter(self):
        # La factory deve restituire JSONFileDeviceExporter per JSON
        factory = ConcreteFileDeviceExporterFactory()
        exporter = factory.get_file_device_exporter(AllowedDeviceFileExtension.JSON)
        assert isinstance(exporter, JSONFileDeviceExporter)

    def test_restituisce_csv_exporter(self):
        # La factory deve restituire CSVFileDeviceExporter per CSV
        factory = ConcreteFileDeviceExporterFactory()
        exporter = factory.get_file_device_exporter(AllowedDeviceFileExtension.CSV)
        assert isinstance(exporter, CSVFileDeviceExporter)

    def test_formato_non_supportato_lancia_valueerror(self):
        # Un formato non supportato deve lanciare ValueError
        factory = ConcreteFileDeviceExporterFactory()
        with pytest.raises(ValueError):
            factory.get_file_device_exporter("pdf")