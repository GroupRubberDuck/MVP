import io
import json
import pytest

from adapters.outbound.device.importer.json_file_device_importer import JSONFileDeviceImporter
from core.ports.outbound.device.exceptions import InvalidFileFormatError


def _to_stream(data: dict) -> io.BytesIO:
    return io.BytesIO(json.dumps(data).encode())


def _base_data(**overrides) -> dict:
    base = {
        "device_id": "DEV-001",
        "standard_id": "STD-001",
        "name": "Router",
        "os": "Linux",
        "description": "Test",
        "assets": [],
    }
    base.update(overrides)
    return base


@pytest.fixture
def importer() -> JSONFileDeviceImporter:
    return JSONFileDeviceImporter()


class TestJSONFileDeviceImporter:

    def test_parses_valid_json(self, importer):
        """
        Dato un flusso di byte contenente un JSON valido con tutti i campi obbligatori di un dispositivo (Given),
        quando l'importer JSON esegue il parsing tramite parse_device_file (When),
        allora deve restituire un oggetto Device con ID e standard_id correttamente estratti dal documento (Then).
        """
        device = importer.parse_device_file(_to_stream(_base_data()))
        assert device.id == "DEV-001"
        assert device.standard_id == "STD-001"

    def test_standard_id_read_from_file(self, importer):
        """
        Dato un file JSON in cui il campo standard_id è valorizzato con un codice personalizzato 'XYZ' (Given),
        quando l'importer deserializza e costruisce il dispositivo (When),
        allora la proprietà standard_id dell'oggetto Device deve riflettere esattamente il valore letto dal file (Then).
        """
        device = importer.parse_device_file(_to_stream(_base_data(standard_id="XYZ")))
        assert device.standard_id == "XYZ"

    def test_parses_device_with_assets(self, importer):
        """
        Dato un JSON contenente un array assets con un singolo asset definito da ID 'A1' e relativi campi (Given),
        quando l'importer completa il parsing dell'intero documento (When),
        allora l'asset deve essere accessibile nella collezione del dispositivo tramite la chiave 'A1' (Then).
        """

        asset = {"id": "A1", "name": "WiFi", "asset_type": "network",
                 "description": "d", "evaluations": []}
        device = importer.parse_device_file(_to_stream(_base_data(assets=[asset])))
        assert "A1" in device.assets

    def test_parses_device_with_evaluations(self, importer):
        """
        Dato un asset che include una evaluation con requirement_id 'REQ-1', un evaluation_map contenente la scelta del nodo N1 e una justification (Given),
        quando l'importer JSON deserializza l'intera struttura nidificata (When),
        allora l'evidenza associata al requirement deve essere recuperabile e contenere la scelta del nodo N1 correttamente valorizzata a True (Then).
        """
        evaluation = {"requirement_id": "REQ-1",
                      "evaluation_map": {"N1": True}, "justification": "ok"}
        asset = {"id": "A1", "name": "WiFi", "asset_type": "network",
                 "description": "d", "evaluations": [evaluation]}
        device = importer.parse_device_file(_to_stream(_base_data(assets=[asset])))
        assert device.assets["A1"].get_evidence("REQ-1").node_choices["N1"] is True

    def test_raises_invalid_format_on_malformed_json(self, importer):
        """
        Dato un flusso di byte contenente una stringa JSON sintatticamente non valida e non interpretabile (Given),
        quando l'importer tenta di decodificare il contenuto come JSON (When),
        allora deve intercettare l'errore di parsing e sollevare un'eccezione InvalidFileFormatError (Then).
        """
        with pytest.raises(InvalidFileFormatError):
            importer.parse_device_file(io.BytesIO(b"{not valid json"))