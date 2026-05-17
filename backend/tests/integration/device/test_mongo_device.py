import pytest
from core.domain.evaluation_object.device import Device
from core.ports.outbound.device.exceptions import DeviceNotFoundError

class TestMongoDeviceAdapterCRUD:

    def test_register_e_find_by_id(self, device_adapter, device_with_asset):
        device_adapter.register(device_with_asset)
        retrieved = device_adapter.find_by_id(device_with_asset.id)
        assert retrieved.id == device_with_asset.id
        assert retrieved.name == device_with_asset.name
        assert retrieved.os == device_with_asset.os
        assert retrieved.description == device_with_asset.description
        assert retrieved.standard_id == device_with_asset.standard_id

    def test_round_trip_asset(self, device_adapter, device_with_asset):
        device_adapter.register(device_with_asset)
        retrieved = device_adapter.find_by_id(device_with_asset.id)
        assert len(retrieved.assets) == 1
        original_asset = list(device_with_asset.assets.values())[0]
        retrieved_asset = list(retrieved.assets.values())[0]
        assert retrieved_asset.id == original_asset.id
        assert retrieved_asset.anagraphic.name == original_asset.anagraphic.name
        assert retrieved_asset.anagraphic.asset_type == original_asset.anagraphic.asset_type
        original_ev = original_asset.proprieties.get_evidence("REQ-001")
        retrieved_ev = retrieved_asset.proprieties.get_evidence("REQ-001")
        assert retrieved_ev is not None
        assert retrieved_ev.justification == original_ev.justification
        assert dict(retrieved_ev.node_choices) == dict(original_ev.node_choices)

    def test_save_and_update_device(self, device_adapter, device_with_asset):
        device_adapter.register(device_with_asset)
        device_with_asset.update_info(name="Firewall Aggiornato", os="Windows")
        device_adapter.save_device(device_with_asset)
        updated = device_adapter.find_by_id(device_with_asset.id)
        assert updated.name == "Firewall Aggiornato"
        assert updated.os == "Windows"
        # se si prova a salvare un dispositivo non registrato
        unregistered = Device.create(
        device_id="device-non-registrato",
        standard_id="STD-001",
        name="Ghost",
        os="Linux",
        description="Mai registrato",
        )
        with pytest.raises(DeviceNotFoundError):
            device_adapter.save_device(unregistered)

    def test_delete_device(self, device_adapter, device_with_asset):
        device_adapter.register(device_with_asset)
        device_adapter.delete(device_with_asset.id)
        with pytest.raises(DeviceNotFoundError):
            device_adapter.find_by_id(device_with_asset.id)

    def test_find_all(self, device_adapter, device_with_asset):
        device_adapter.register(device_with_asset)
        summaries = device_adapter.find_all()
        assert len(summaries) == 1
        s = summaries[0]
        assert s.device_id == device_with_asset.id
        assert s.name == device_with_asset.name
        assert not hasattr(s, "assets")

    def test_register_duplicato(self, device_adapter, device_with_asset):
# Registrare due volte lo stesso device lancia un'eccezione di duplicato.
        device_adapter.register(device_with_asset)
        with pytest.raises(Exception):  
            device_adapter.register(device_with_asset)

    def test_find_id_inesistente(self, device_adapter):
        with pytest.raises(DeviceNotFoundError):
            device_adapter.find_by_id("id-che-non-esiste")
        
    def test_device_senza_asset(self, device_adapter):
        device = Device.create(
            device_id="bare-device",
            standard_id="STD-001",
            name="Bare",
            os="FreeRTOS",
            description="Nessun asset",
        )
        device_adapter.register(device)
        retrieved = device_adapter.find_by_id("bare-device")
        assert len(retrieved.assets) == 0