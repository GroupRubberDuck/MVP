import pytest
import xml.etree.ElementTree as ET
import json
import csv
import io
from core.domain.evaluation_object.device import Device
from core.domain.evaluation_object.asset.asset import Asset
from core.domain.evaluation_object.asset.asset_anagraphic import AssetAnagraphic
from core.domain.evaluation_object.asset.asset_proprieties import AssetProprieties
from core.domain.evaluation_object.asset.asset_evidence import AssetEvidence
from core.domain.evaluation_object.asset.asset_type import AssetType
from core.domain.evaluation_object.allowed_device_file_extension import AllowedDeviceFileExtension
from adapters.outbound.device.exporter.xml_file_device_exporter import XMLFileDeviceExporter
from adapters.outbound.device.exporter.json_file_device_exporter import JSONFileDeviceExporter
from adapters.outbound.device.exporter.csv_file_device_exporter import CSVFileDeviceExporter
from adapters.outbound.device.exporter.concrete_file_device_exporter_factory import ConcreteFileDeviceExporterFactory
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


#  XML


class TestXMLFileDeviceExporter:

    def test_output_e_stream(self, device):
        """
        Dato un device valido, 
        quando viene esportato in formato XML, 
        allora il risultato restituito deve essere un flusso in memoria (BytesIO) contenente byte.
        """
        stream = XMLFileDeviceExporter().generate_device_file(device)
        assert isinstance(stream, io.BytesIO)
        result = stream.read()
        assert isinstance(result, bytes)

    def test_contiene_device_id(self, device):
        """
        Dato un device popolato, 
        quando viene esportato in XML, 
        allora il nodo radice del documento deve contenere l'attributo corretto 'device_id'.
        """
        # L'attributo deve chiamarsi device_id
        result = XMLFileDeviceExporter().generate_device_file(device).read()
        root = ET.fromstring(result)
        assert root.attrib["device_id"] == "device-1"

    def test_asset_appiattito(self, device):
        """
        Dato un device contenente un asset, 
        quando viene generato l'XML, 
        allora la struttura dell'asset deve risultare appiattita 
        (i dati anagrafici come 'name' devono essere figli diretti di <asset>, omettendo il nodo <anagraphic>).
        """
        # Il nome dell'asset deve essere figlio diretto di <asset>
        result = XMLFileDeviceExporter().generate_device_file(device).read()
        root = ET.fromstring(result)
        
        # Cerchiamo il tag <name> dentro <asset>
        name_el = root.find("assets/asset/name")
        assert name_el is not None
        assert name_el.text == "Router"
        
        # Verifichiamo che NON esista più il tag <anagraphic>
        assert root.find("assets/asset/anagraphic") is None

    def test_asset_ha_tipo_corretto(self, device):
        """
        Dato un device con un asset di tipo NETWORK, 
        quando viene esportato in XML, 
        allora il tag <asset_type> deve essere formattato correttamente come stringa (es. 'network').
        """
        result = XMLFileDeviceExporter().generate_device_file(device).read()
        root = ET.fromstring(result)
        asset_type = root.find("assets/asset/asset_type").text
        assert asset_type == "network"

    def test_contiene_valutazioni(self, device):
        """
        Dato un device con un'evidenza associata, 
        quando viene esportato in XML, 
        allora deve essere presente un nodo <evaluations> che racchiude le relative <evaluation>.
        """
        # Il tag deve essere <evaluations> e contenere <evaluation>
        result = XMLFileDeviceExporter().generate_device_file(device).read()
        root = ET.fromstring(result)
        evals = root.findall("assets/asset/evaluations/evaluation")
        assert len(evals) == 1

    def test_evidenza_ha_evaluation_map(self, device):
        """
        Dato un device le cui evidenze contengono scelte multiple (node_choices), 
        quando viene esportato in XML, 
        allora tali scelte devono essere mappate correttamente sotto il nodo <evaluation_map>.
        """
        # Il tag deve essere <evaluation_map>
        result = XMLFileDeviceExporter().generate_device_file(device).read()
        root = ET.fromstring(result)
        choices = root.findall("assets/asset/evaluations/evaluation/evaluation_map/choice")
        assert len(choices) == 2
        assert choices[0].attrib["node_id"] == "node-1"


# JSON

class TestJSONFileDeviceExporter:

    def test_output_e_stream(self, device):
        """
        Dato un device valido, 
        quando viene esportato in formato JSON, 
        allora il risultato restituito deve essere un flusso in memoria (BytesIO) contenente byte.
        """
        stream = JSONFileDeviceExporter().generate_device_file(device)
        assert isinstance(stream, io.BytesIO)
        result = stream.read()
        assert isinstance(result, bytes)

    def test_json_valido(self, device):
        """
        Dato un device, 
        quando viene esportato in JSON, 
        allora il flusso in uscita deve essere decodificabile come un oggetto JSON valido (dizionario).
        """
        # Il risultato deve essere JSON valido
        result = JSONFileDeviceExporter().generate_device_file(device).read()
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_contiene_id_device(self, device):
        """
        Dato un device, 
        quando viene esportato in JSON, 
        allora la radice del documento JSON deve includere la chiave 'device_id' corretta.
        """
        # Il campo device_id deve corrispondere a quello del device
        result = JSONFileDeviceExporter().generate_device_file(device).read()
        data = json.loads(result)
        assert data["device_id"] == "device-1"

    def test_contiene_nome_device(self, device):
        """
        Dato un device, 
        quando viene esportato in JSON, 
        allora la radice del documento JSON deve includere il nome (name) del dispositivo.
        """
        # Il campo name deve essere presente
        result = JSONFileDeviceExporter().generate_device_file(device).read()
        data = json.loads(result)
        assert data["name"] == "Test Device"

    def test_contiene_asset(self, device):
        """
        Dato un device contenente un singolo asset, 
        quando viene esportato in JSON, 
        allora la lista 'assets' all'interno del JSON deve avere esattamente lunghezza 1.
        """
        # Deve esserci esattamente 1 asset
        result = JSONFileDeviceExporter().generate_device_file(device).read()
        data = json.loads(result)
        assert len(data["assets"]) == 1

    def test_asset_ha_tipo_corretto(self, device):
        """
        Dato un device, 
        quando viene esportato in JSON, 
        allora i dati anagrafici dell'asset devono risultare appiattiti 
        e il campo 'asset_type' deve essere una stringa valida (es. 'network').
        """
        # Il tipo dell'asset deve essere serializzato come stringa (e appiattito)
        result = JSONFileDeviceExporter().generate_device_file(device).read()
        data = json.loads(result)
        # Non c'è più ["anagraphic"], la chiave è al primo livello dell'asset
        assert data["assets"][0]["asset_type"] == "network"

    def test_contiene_evidenza(self, device):
        """
        Dato un device con evidenze associate all'asset, 
        quando viene esportato in JSON, 
        allora la lista 'evaluations' dell'asset deve essere regolarmente popolata.
        """
        # Deve esserci esattamente 1 valutazione (evaluations)
        result = JSONFileDeviceExporter().generate_device_file(device).read()
        data = json.loads(result)
        assert len(data["assets"][0]["evaluations"]) == 1

    def test_evidenza_ha_evaluation_map(self, device):
        """
        Dato un device con un'evidenza che presenta scelte per nodi diversi, 
        quando viene esportato in JSON, 
        allora le scelte devono essere riportate come coppie chiave-valore sotto l'oggetto 'evaluation_map'.
        """
        # Le evaluation_map devono essere serializzate come dizionario
        result = JSONFileDeviceExporter().generate_device_file(device).read()
        data = json.loads(result)
        # La chiave è evaluation_map invece del vecchio node_choices
        choices = data["assets"][0]["evaluations"][0]["evaluation_map"]
        assert choices["node-1"] is True
        assert choices["node-2"] is False

#  CSV


class TestCSVFileDeviceExporter:

    def test_output_e_stream(self, device):
        """
        Dato un device valido, 
        quando viene esportato in formato CSV, 
        allora il risultato restituito deve essere un flusso in memoria (BytesIO) contenente byte.
        """
        stream = CSVFileDeviceExporter().generate_device_file(device)
        assert isinstance(stream, io.BytesIO)
        result = stream.read()
        assert isinstance(result, bytes)

    def test_header_corretto(self, device):
        """
        Dato un device, 
        quando viene esportato in CSV, 
        allora la prima riga (header) deve contenere i nomi corretti 
        dei campi appiattiti necessari all'importer (es. 'device_id', 'asset_name', ecc.).
        """
        # Assicura che le intestazioni piatte siano corrette per l'importer
        result = CSVFileDeviceExporter().generate_device_file(device).read()
        text = result.decode("utf-8")
        reader = csv.DictReader(io.StringIO(text))
        
        assert reader.fieldnames is not None
        assert "device_id" in reader.fieldnames
        assert "asset_name" in reader.fieldnames
        assert "requirement_id" in reader.fieldnames
        assert "node_id" in reader.fieldnames

    def test_righe_piatte_esportate_correttamente(self, device):
        """
        Dato un device con 1 asset, 1 evidenza e 2 scelte per i nodi, 
        quando viene esportato in CSV, 
        allora devono essere generate esattamente 2 righe piatte, ognuna relativa a un nodo valutato.
        """
        # Il test_device ha 1 asset, 1 evidenza e 2 node_choices (node-1, node-2).
        # Questo significa che il CSV piatto generato deve avere esattamente 2 righe.
        result = CSVFileDeviceExporter().generate_device_file(device).read()
        text = result.decode("utf-8")
        reader = list(csv.DictReader(io.StringIO(text)))
        
        assert len(reader) == 2
        
        # Verifichiamo la prima riga (node-1)
        row1 = reader[0]
        assert row1["device_id"] == "device-1"
        assert row1["name"] == "Test Device"
        assert row1["asset_id"] == "asset-1"
        assert row1["asset_type"] == "network"
        assert row1["requirement_id"] == "req-1"
        assert row1["node_id"] == "node-1"
        assert row1["node_value"] == "true"
        assert row1["justification"] == "Motivazione test"
        
        # Verifichiamo la seconda riga (node-2)
        row2 = reader[1]
        assert row2["node_id"] == "node-2"
        assert row2["node_value"] == "false"
        assert row2["justification"] == "Motivazione test"

# Factory


class TestConcreteFileDeviceExporterFactory:
    def test_restituisce_xml_exporter(self):
        """
        Data una richiesta per l'estensione XML, 
        quando la factory viene invocata, 
        allora deve istanziare e restituire un XMLFileDeviceExporter.
        """
        # La factory deve restituire XMLFileDeviceExporter per XML
        factory = ConcreteFileDeviceExporterFactory()
        exporter = factory.get_file_device_exporter(AllowedDeviceFileExtension.XML)
        assert isinstance(exporter, XMLFileDeviceExporter)

    def test_restituisce_json_exporter(self):
        """
        Data una richiesta per l'estensione JSON, 
        quando la factory viene invocata, 
        allora deve istanziare e restituire un JSONFileDeviceExporter.
        """
        # La factory deve restituire JSONFileDeviceExporter per JSON
        factory = ConcreteFileDeviceExporterFactory()
        exporter = factory.get_file_device_exporter(AllowedDeviceFileExtension.JSON)
        assert isinstance(exporter, JSONFileDeviceExporter)

    def test_restituisce_csv_exporter(self):
        """
        Data una richiesta per l'estensione CSV, 
        quando la factory viene invocata, 
        allora deve istanziare e restituire un CSVFileDeviceExporter.
        """
        # La factory deve restituire CSVFileDeviceExporter per CSV
        factory = ConcreteFileDeviceExporterFactory()
        exporter = factory.get_file_device_exporter(AllowedDeviceFileExtension.CSV)
        assert isinstance(exporter, CSVFileDeviceExporter)

    def test_formato_non_supportato_lancia_valueerror(self):
        """
        Data una richiesta per un formato non supportato (es. 'pdf'), 
        quando la factory tenta di risolvere l'exporter, 
        allora deve sollevare un'eccezione ValueError.
        """
        # Un formato non supportato deve lanciare ValueError
        factory = ConcreteFileDeviceExporterFactory()
        with pytest.raises(ValueError):
            factory.get_file_device_exporter("pdf")
