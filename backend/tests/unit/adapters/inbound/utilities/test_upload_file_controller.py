import io
import pytest
from unittest.mock import MagicMock

from adapters.inbound.utilities.upload_file_controller import UploadFileController
from core.services.device.allowed_device_extensions import AllowedDeviceFileExtension


class TestGetHttpFileExtension:

    def test_returns_csv_extension(self):
        """
        Dato un nome file con estensione '.csv' (Given),
        quando viene invocato il metodo per estrarre l'estensione (When),
        allora il controller deve identificare e restituire l'enum AllowedDeviceFileExtension.CSV (Then).
        """
        result = UploadFileController.get_http_file_extension("device.csv")
        assert result == AllowedDeviceFileExtension.CSV

    def test_returns_json_extension(self):
        """
        Dato un nome file con estensione '.json' (Given),
        quando viene invocato il metodo per estrarre l'estensione (When),
        allora il controller deve identificare e restituire l'enum AllowedDeviceFileExtension.JSON (Then).
        """
        result = UploadFileController.get_http_file_extension("device.json")
        assert result == AllowedDeviceFileExtension.JSON

    def test_returns_xml_extension(self):
        """
        Dato un nome file con estensione '.xml' (Given),
        quando viene invocato il metodo per estrarre l'estensione (When),
        allora il controller deve identificare e restituire l'enum AllowedDeviceFileExtension.XML (Then).
        """
        result = UploadFileController.get_http_file_extension("device.xml")
        assert result == AllowedDeviceFileExtension.XML

    def test_extension_is_case_insensitive(self):
        """
        Dato un nome file con estensione scritta in maiuscolo (es. '.CSV') (Given),
        quando il controller analizza la stringa (When),
        allora l'operazione deve essere case-insensitive e restituire correttamente l'enum associato (Then).
        """
        result = UploadFileController.get_http_file_extension("device.CSV")
        assert result == AllowedDeviceFileExtension.CSV

    def test_raises_when_no_extension(self):
        """
        Dato un nome file completamente privo di estensione e di punti (Given),
        quando si tenta di estrarre il formato del file (When),
        allora il controller deve sollevare un ValueError indicando che il file non ha un'estensione (Then).
        """
        with pytest.raises(ValueError, match="non ha un'estensione"):
            UploadFileController.get_http_file_extension("device")

    def test_raises_when_unsupported_extension(self):
        """
        Dato un nome file con un'estensione non consentita dal sistema (es. '.txt') (Given),
        quando viene valutata la sua estensione (When),
        allora il controller deve sollevare un ValueError indicando che il formato non è supportato (Then).
        """
        with pytest.raises(ValueError, match="non supportata"):
            UploadFileController.get_http_file_extension("device.txt")

    def test_uses_last_dot_segment(self):
        """
        Dato un nome file complesso che contiene punti intermedi (es. 'my.device.json') (Given),
        quando il controller estrae l'estensione (When),
        allora deve considerare unicamente l'ultimo segmento dopo il punto finale (Then).
        """
        result = UploadFileController.get_http_file_extension("my.device.json")
        assert result == AllowedDeviceFileExtension.JSON


class TestGetHttpFilePayload:

    def test_returns_file_storage_stream(self):
        """
        Dato un oggetto FileStorage (tipico dei file ricevuti tramite Flask) contenente uno stream di byte (Given),
        quando il controller tenta di estrarre il payload (When),
        allora deve restituire esattamente l'oggetto stream (BytesIO) incapsulato al suo interno (Then).
        """
        stream = io.BytesIO(b"contenuto")
        file_storage = MagicMock()
        file_storage.stream = stream

        result = UploadFileController.get_http_file_payload(file_storage)

        assert result is stream