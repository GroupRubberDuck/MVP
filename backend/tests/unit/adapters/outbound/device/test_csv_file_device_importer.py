import io
import pytest

from adapters.outbound.device.importer.csv_file_device_importer import (
    CSVFileDeviceImporter,
)
from core.ports.outbound.device.exceptions import EmptyFileError, InvalidFileFormatError


_HEADER = "device_id,standard_id,name,os,description,asset_id,asset_name,asset_type,asset_description\n"


def _to_stream(*rows: str) -> io.BytesIO:
    content = _HEADER + "".join(rows)
    return io.BytesIO(content.encode())


def _row(
    device_id="DEV-001",
    standard_id="STD-001",
    name="Router",
    os="Linux",
    description="Test",
    asset_id="A1",
    asset_name="WiFi",
    asset_type="network",
    asset_description="desc",
) -> str:
    return f"{device_id},{standard_id},{name},{os},{description},{asset_id},{asset_name},{asset_type},{asset_description}\n"


@pytest.fixture
def importer() -> CSVFileDeviceImporter:
    return CSVFileDeviceImporter()


class TestCSVFileDeviceImporter:
    def test_parses_single_row(self, importer):
        """
        Dato un file CSV contenente l'header e una singola riga di dati dispositivo valida (Given),
        quando l'importer esegue il parsing tramite parse_device_file (When),
        allora deve restituire un oggetto Device con ID e standard_id correttamente estratti dalla riga (Then).
        """
        device = importer.parse_device_file(_to_stream(_row()))
        assert device.id == "DEV-001"
        assert device.standard_id == "STD-001"

    def test_single_asset(self, importer):
        """
        Dato un file CSV con una riga che specifica un asset identificato da 'A1' (Given),
        quando il parsing viene completato con successo (When),
        allora il dizionario degli asset del dispositivo risultante deve contenere la chiave 'A1' (Then).
        """
        device = importer.parse_device_file(_to_stream(_row(asset_id="A1")))
        assert "A1" in device.assets

    def test_groups_multiple_rows_into_one_device(self, importer):
        """
        Date due righe CSV con lo stesso device_id ma asset_id diversi ('A1' e 'A2') (Given),
        quando l'importer processa il file (When),
        allora deve aggregare entrambi gli asset in un unico dispositivo, risultando in una collezione di due asset distinti (Then).
        """
        device = importer.parse_device_file(
            _to_stream(_row(asset_id="A1"), _row(asset_id="A2"))
        )
        assert len(device.assets) == 2

    def test_deduplicates_same_asset_id(self, importer):
        """
        Date due righe CSV che fanno riferimento allo stesso dispositivo e condividono il medesimo asset_id 'A1' (Given),
        quando l'importer aggrega le righe in un unico dispositivo (When),
        allora l'asset duplicato deve essere rilevato e scartato, mantenendo un solo elemento nella collezione degli asset (Then).
        """
        device = importer.parse_device_file(
            _to_stream(_row(asset_id="A1"), _row(asset_id="A1"))
        )
        assert len(device.assets) == 1

    def test_raises_empty_file_on_no_rows(self, importer):
        """
        Dato un flusso CSV contenente solo la riga di intestazione e nessuna riga dati (Given),
        quando l'importer tenta di eseguire il parsing (When),
        allora deve sollevare un'eccezione EmptyFileError per segnalare l'assenza di contenuto elaborabile (Then).
        """
        stream = io.BytesIO(_HEADER.encode())
        with pytest.raises(EmptyFileError):
            importer.parse_device_file(stream)

    def test_raises_invalid_format_on_encoding_error(self, importer):
        """
        Dato un flusso di byte corrotto o con encoding non UTF-8 che non può essere decodificato correttamente (Given),
        quando l'importer tenta di leggerlo e interpretarlo come CSV (When),
        allora deve intercettare l'errore di decodifica e sollevare un'eccezione InvalidFileFormatError (Then).
        """
        stream = io.BytesIO(b"\xff\xfe\x00 contenuto non utf-8")
        with pytest.raises(InvalidFileFormatError):
            importer.parse_device_file(stream)
