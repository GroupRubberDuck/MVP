import pytest

from adapters.outbound.device.exporter.json_file_device_exporter import JSONFileDeviceExporter
from adapters.outbound.device.importer.json_file_device_importer import JSONFileDeviceImporter
from adapters.outbound.device.exporter.xml_file_device_exporter import XMLFileDeviceExporter
from adapters.outbound.device.importer.xml_file_device_importer import XMLFileDeviceImporter

from adapters.outbound.device.exporter.csv_file_device_exporter import CSVFileDeviceExporter
from adapters.outbound.device.importer.csv_file_device_importer import CSVFileDeviceImporter
from core.domain.evaluation_object.device import Device
from core.domain.evaluation_object.asset.asset import Asset
from core.domain.evaluation_object.asset.asset_anagraphic import AssetAnagraphic
from core.domain.evaluation_object.asset.asset_proprieties import AssetProprieties
from core.domain.evaluation_object.asset.asset_evidence import AssetEvidence
from core.domain.evaluation_object.asset.asset_type import AssetType
from types import MappingProxyType


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


class TestDeviceImportExport:
    def test_json_round_trip(self, device):
        """
        Verifica che esportando un Device in JSON e re-importandolo,
        i dati rimangano perfettamente intatti e compatibili.
        """
        exporter = JSONFileDeviceExporter()

        exported_stream = exporter.generate_device_file(device)

        exported_stream.seek(0)

        importer = JSONFileDeviceImporter()

        imported_device = importer.parse_device_file(exported_stream)

        assert imported_device.id == device.id
        assert imported_device.name == device.name
        assert imported_device.standard_id == device.standard_id

        assert len(imported_device.assets) == len(device.assets)

        original_asset = list(device.assets.values())[0]
        imported_asset = list(imported_device.assets.values())[0]

        assert imported_asset.id == original_asset.id
        assert imported_asset.anagraphic.name == original_asset.anagraphic.name
        assert (
            imported_asset.anagraphic.asset_type == original_asset.anagraphic.asset_type
        )

        # Verifica Evidenze
        assert len(imported_asset.proprieties.evidences) == len(
            original_asset.proprieties.evidences
        )

        original_evidence = list(original_asset.proprieties.evidences.values())[0]
        imported_evidence = list(imported_asset.proprieties.evidences.values())[0]

        assert imported_evidence.requirement_id == original_evidence.requirement_id
        assert imported_evidence.justification == original_evidence.justification

        # Verifica profonda delle node_choices (la evaluation_map)
        for node_id, original_value in original_evidence.node_choices.items():
            assert imported_evidence.node_choices[node_id] == original_value


    def test_xml_round_trip(self, device):
        """
        Verifica che esportando un Device in XML e re-importandolo,
        i dati rimangano perfettamente intatti e compatibili.
        """
        # --- 1. EXPORT ---
        exporter = XMLFileDeviceExporter()
        exported_stream = exporter.generate_device_file(device)
        exported_stream.seek(0)

        # --- 2. IMPORT ---
        importer = XMLFileDeviceImporter()
        imported_device = importer.parse_device_file(exported_stream)

        # --- 3. ASSERT ---
        assert imported_device.id == device.id
        assert imported_device.name == device.name
        assert imported_device.standard_id == device.standard_id

        assert len(imported_device.assets) == len(device.assets)

        original_asset = list(device.assets.values())[0]
        imported_asset = list(imported_device.assets.values())[0]

        assert imported_asset.id == original_asset.id
        assert imported_asset.anagraphic.name == original_asset.anagraphic.name
        assert imported_asset.anagraphic.asset_type == original_asset.anagraphic.asset_type

        assert len(imported_asset.proprieties.evidences) == len(
            original_asset.proprieties.evidences
        )

        original_evidence = list(original_asset.proprieties.evidences.values())[0]
        imported_evidence = list(imported_asset.proprieties.evidences.values())[0]

        assert imported_evidence.requirement_id == original_evidence.requirement_id
        assert imported_evidence.justification == original_evidence.justification

        for node_id, original_value in original_evidence.node_choices.items():
            assert imported_evidence.node_choices[node_id] == original_value


    def test_csv_round_trip(self, device):
        """
        Verifica che esportando un Device in CSV e re-importandolo,
        i dati rimangano perfettamente intatti e compatibili.
        """
        # --- 1. EXPORT ---
        exporter = CSVFileDeviceExporter()
        exported_stream = exporter.generate_device_file(device)
        exported_stream.seek(0)

        # --- 2. IMPORT ---
        importer = CSVFileDeviceImporter()
        imported_device = importer.parse_device_file(exported_stream)

        # --- 3. ASSERT ---
        assert imported_device.id == device.id
        assert imported_device.name == device.name
        assert imported_device.standard_id == device.standard_id

        assert len(imported_device.assets) == len(device.assets)

        original_asset = list(device.assets.values())[0]
        imported_asset = list(imported_device.assets.values())[0]

        assert imported_asset.id == original_asset.id
        assert imported_asset.anagraphic.name == original_asset.anagraphic.name
        assert imported_asset.anagraphic.asset_type == original_asset.anagraphic.asset_type

        assert len(imported_asset.proprieties.evidences) == len(
            original_asset.proprieties.evidences
        )

        original_evidence = list(original_asset.proprieties.evidences.values())[0]
        imported_evidence = list(imported_asset.proprieties.evidences.values())[0]

        assert imported_evidence.requirement_id == original_evidence.requirement_id
        assert imported_evidence.justification == original_evidence.justification

        for node_id, original_value in original_evidence.node_choices.items():
            assert imported_evidence.node_choices[node_id] == original_value
