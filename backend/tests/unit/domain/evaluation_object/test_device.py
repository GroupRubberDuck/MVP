import pytest

from core.domain.evaluation_object.device import Device
from core.domain.evaluation_object.asset import Asset
from core.domain.evaluation_object.answer import Answer
from core.domain.evaluation_object.asset_type import AssetType

class TestDevice:
                """Test di creazione della classe Device"""
                @pytest.mark.requirement("REQ-DEV-01")
                @pytest.mark.priority("high")
                @pytest.mark.type("unità")
                def test_device_creation(self):
                        """
                        Un Device può essere creato solo con id, standard_id, name, os e description.
                        """
                        device = Device(device_id="device-1", standard_id="standard-1", name="Device 1", os="Android", description="Un dispositivo di test")
                        assert device.id == "device-1"
                        assert device.standard_id == "standard-1"
                        assert device.name == "Device 1"
                        assert device.os == "Android"
                        assert device.description == "Un dispositivo di test"

                @pytest.mark.requirement("REQ-DEV-01")
                @pytest.mark.priority("high")
                @pytest.mark.type("unità")
                def test_device_creation_with_assets(self):
                        """
                        Un Device può essere creato con un dizionario di asset.
                        """
                        device = Device(
                            device_id="device-1",
                            standard_id="standard-1",
                            name="Device 1",
                            os="Android",
                            description="Un dispositivo di test",
                            assets=[ Asset(
                                asset_id="asset-1",
                                name="Asset 1",
                                asset_type=AssetType.SECURITY,
                                description="Un asset di test"
                            )]
                        )
                        assert device.id == "device-1"
                        assert device.standard_id == "standard-1"
                        assert device.name == "Device 1"
                        assert device.os == "Android"
                        assert device.description == "Un dispositivo di test"
                        assert "asset-1" in device._assets  
                        assert device._assets["asset-1"].id == "asset-1"


                @pytest.mark.requirement("REQ-DEV-01")
                @pytest.mark.priority("high")
                @pytest.mark.type("unità")
                def test_get_asset_by_id(self):
                        """
                        Il metodo _get_asset_by_id restituisce l'asset corretto o solleva un'eccezione se non trovato.
                        """
                        device = Device(device_id="device-1", standard_id="standard-1", name="Device 1", os="Android", description="Un dispositivo di test")
                        asset = Asset(asset_id="asset-1", name="Asset 1", asset_type=AssetType.SECURITY, description="Un asset di test")
                        device.add_asset(asset)

                        # Verifichiamo che l'asset venga restituito correttamente
                        retrieved_asset = device._get_asset_by_id("asset-1")
                        assert retrieved_asset.id == "asset-1"

                        # Verifichiamo che venga sollevata un'eccezione se l'asset non esiste
                        with pytest.raises(Exception):
                            device._get_asset_by_id("non-existent-asset")


                @pytest.mark.requirement("REQ-DEV-01")
                @pytest.mark.priority("high")
                @pytest.mark.type("unità")
                def test_get_asset_by_id_non_existent(self):
                        """
                        Il metodo _get_asset_by_id solleva un'eccezione se si tenta di ottenere un asset che non esiste.
                        """
                        device = Device(device_id="device-1", standard_id="standard-1", name="Device 1", os="Android", description="Un dispositivo di test")
                        with pytest.raises(Exception):
                            device._get_asset_by_id("non-existent-asset")



                @pytest.mark.requirement("REQ-DEV-01")
                @pytest.mark.priority("high")
                @pytest.mark.type("unità")
                def test_setter_methods(self):
                        """
                        I setter di Device funzionano correttamente.
                        """
                        device = Device(device_id="device-1", standard_id="standard-1", name="Device 1", os="Android", description="Un dispositivo di test")
                        device.set_name("Updated Device")
                        device.set_os("iOS")
                        device.set_description("Dispositivo aggiornato")

                        assert device.name == "Updated Device"
                        assert device.os == "iOS"
                        assert device.description == "Dispositivo aggiornato"

                @pytest.mark.requirement("REQ-DEV-01")
                @pytest.mark.priority("high")
                @pytest.mark.type("unità")
                def test_getter_methods(self):
                        """
                        I getter di Device funzionano correttamente.
                        """
                        device = Device(device_id="device-1", standard_id="standard-1", name="Device 1", os="Android", description="Un dispositivo di test")
                        assert device.id == "device-1"
                        assert device.standard_id == "standard-1"
                        assert device.name == "Device 1"
                        assert device.os == "Android"
                        assert device.description == "Un dispositivo di test"

                @pytest.mark.requirement("REQ-DEV-01")
                @pytest.mark.priority("high")
                @pytest.mark.type("unità")
                def test_add_duplicate_asset(self):
                        """
                        Il metodo add_asset solleva un'eccezione se si tenta di aggiungere un asset con un id già esistente.
                        """
                        device = Device(device_id="device-1", standard_id="standard-1", name="Device 1", os="Android", description="Un dispositivo di test")
                        asset = Asset(asset_id="asset-1", name="Asset 1", asset_type=AssetType.SECURITY, description="Un asset di test")
                        device.add_asset(asset)

                        duplicate_asset = Asset(asset_id="asset-1", name="Duplicate Asset", asset_type=AssetType.NETWORK, description="Un asset duplicato")
                        with pytest.raises(Exception):
                            device.add_asset(duplicate_asset)

                @pytest.mark.requirement("REQ-DEV-01")
                @pytest.mark.priority("high")
                @pytest.mark.type("unità")
                def test_add_asset(self):
                        """
                        Il metodo add_asset aggiunge un nuovo asset al dispositivo.
                        """
                        device = Device(device_id="device-1", standard_id="standard-1", name="Device 1", os="Android", description="Un dispositivo di test")
                        asset = Asset(asset_id="asset-1", name="Asset 1", asset_type=AssetType.SECURITY, description="Un asset di test")
                        device.add_asset(asset)
                        assert "asset-1" in device._assets
                        assert device._assets["asset-1"].id == "asset-1"


                @pytest.mark.requirement("REQ-DEV-01")
                @pytest.mark.priority("high")
                @pytest.mark.type("unità")
                def test_add_asset_with_existing_id(self):
                        """
                        Il metodo add_asset solleva un'eccezione se si tenta di aggiungere un asset con un id già esistente.
                        """
                        device = Device(device_id="device-1", standard_id="standard-1", name="Device 1", os="Android", description="Un dispositivo di test")
                        asset = Asset(asset_id="asset-1", name="Asset 1", asset_type=AssetType.SECURITY, description="Un asset di test")
                        device.add_asset(asset)

                        duplicate_asset = Asset(asset_id="asset-1", name="Duplicate Asset", asset_type=AssetType.NETWORK, description="Un asset duplicato")
                        with pytest.raises(Exception):
                            device.add_asset(duplicate_asset)

                @pytest.mark.requirement("REQ-DEV-01")
                @pytest.mark.priority("high")
                @pytest.mark.type("unità")
                def test_add_asset_with_different_id(self):
                        """
                        Il metodo add_asset aggiunge un nuovo asset se l'id è diverso da quelli esistenti.
                        """
                        device = Device(device_id="device-1", standard_id="standard-1", name="Device 1", os="Android", description="Un dispositivo di test")
                        asset1 = Asset(asset_id="asset-1", name="Asset 1", asset_type=AssetType.SECURITY, description="Un asset di test")
                        asset2 = Asset(asset_id="asset-2", name="Asset 2", asset_type=AssetType.NETWORK, description="Un altro asset di test")

                        device.add_asset(asset1)
                        device.add_asset(asset2)

                        assert "asset-1" in device._assets
                        assert "asset-2" in device._assets
                        assert device._assets["asset-1"].id == "asset-1"
                        assert device._assets["asset-2"].id == "asset-2"


                @pytest.mark.requirement("REQ-DEV-01")
                @pytest.mark.priority("high")
                @pytest.mark.type("unità")
                def test_remove_asset(self):
                        """
                        Il metodo remove_asset rimuove un asset esistente dal dispositivo.
                        """
                        device = Device(device_id="device-1", standard_id="standard-1", name="Device 1", os="Android", description="Un dispositivo di test")
                        asset = Asset(asset_id="asset-1", name="Asset 1", asset_type=AssetType.SECURITY, description="Un asset di test")
                        device.add_asset(asset)

                        device.remove_asset("asset-1")
                        assert "asset-1" not in device._assets


                @pytest.mark.requirement("REQ-DEV-01")
                @pytest.mark.priority("high")
                @pytest.mark.type("unità")
                def test_remove_non_existent_asset(self):
                        """
                        Il metodo remove_asset solleva un'eccezione se si tenta di rimuovere un asset che non esiste.
                        """
                        device = Device(device_id="device-1", standard_id="standard-1", name="Device 1", os="Android", description="Un dispositivo di test")
                        with pytest.raises(Exception):
                            device.remove_asset("non-existent-asset")




                @pytest.mark.requirement("REQ-DEV-01")
                @pytest.mark.priority("high")
                @pytest.mark.type("unità")
                def test_device_creation_with_duplicated_id_assets(self):
                        """
                        Un Device non può essere creato con un dizionario di asset che contiene id duplicati.
                        """
                        with pytest.raises(Exception):
                            Device(
                                device_id="device-1",
                                standard_id="standard-1",
                                name="Device 1",
                                os="Android",
                                description="Un dispositivo di test",
                                assets=[
                                    Asset(
                                        asset_id="asset-1",
                                        name="Asset 1",
                                        asset_type=AssetType.SECURITY,
                                        description="Un asset di test"
                                    ),
                                    Asset(
                                        asset_id="asset-1",
                                        name="Duplicate Asset",
                                        asset_type=AssetType.NETWORK,
                                        description="Un asset duplicato"
                                    )
                                ]
                            )



                @pytest.mark.requirement("REQ-DEV-01")
                @pytest.mark.priority("high")
                @pytest.mark.type("unità")
                def test_snapshot_creation(self):
                        """
                        Il metodo create_snapshot restituisce un SnapshotDevice con i dati corretti.
                        """
                        device = Device(
                            device_id="device-1",
                            standard_id="standard-1",
                            name="Device 1",
                            os="Android",
                            description="Un dispositivo di test",
                            assets=[ Asset(
                                asset_id="asset-1",
                                name="Asset 1",
                                asset_type=AssetType.SECURITY,
                                description="Un asset di test"
                            )]
                        )
                        snapshot = device.create_snapshot()
                        assert snapshot.id == "device-1"
                        assert snapshot.standard_id == "standard-1"
                        assert snapshot.name == "Device 1"



                @pytest.mark.requirement("REQ-DEV-01")
                @pytest.mark.priority("high")
                @pytest.mark.type("unità")
                def test_snapshot_creation_with_assets(self):
                        """
                        Il metodo create_snapshot restituisce un SnapshotDevice con i dati corretti, inclusi gli asset.
                        """
                        device = Device(
                            device_id="device-1",
                            standard_id="standard-1",
                            name="Device 1",
                            os="Android",
                            description="Un dispositivo di test",
                            assets=[Asset(
                                asset_id="asset-1",
                                name="Asset 1",
                                asset_type=AssetType.SECURITY,
                                description="Un asset di test"
                            )] 
                        )
                        snapshot = device.create_snapshot()
                        assert snapshot.id == "device-1"
                        assert snapshot.standard_id == "standard-1"
                        assert snapshot.name == "Device 1"
                        assert snapshot.os == "Android"
                        assert snapshot.description == "Un dispositivo di test"
                        assert "asset-1" in snapshot.assets
                        assert snapshot.assets["asset-1"].id == "asset-1"       


                @pytest.mark.requirement("REQ-DEV-01")
                @pytest.mark.priority("high")
                @pytest.mark.type("unità")
                def test_summary_snapshot_creation(self):
                        """
                        Il metodo create_summary_snapshot restituisce un SnapshotDeviceSummary con i dati corretti.
                        """
                        device = Device(
                            device_id="device-1",
                            standard_id="standard-1",
                            name="Device 1",
                            os="Android",
                            description="Un dispositivo di test",
                            assets=[Asset(
                                asset_id="asset-1",
                                name="Asset 1",
                                asset_type=AssetType.SECURITY,
                                description="Un asset di test"
                            )]
                        )
                        summary_snapshot = device.create_summary_snapshot()
                        assert summary_snapshot.id == "device-1"
                        assert summary_snapshot.standard_id == "standard-1"
                        assert summary_snapshot.name == "Device 1"



                @pytest.mark.requirement("REQ-DEV-01")
                @pytest.mark.priority("high")
                @pytest.mark.type("unità")
                def test_summary_snapshot_creation_with_assets(self):
                        """
                        Il metodo create_summary_snapshot restituisce un SnapshotDeviceSummary con i dati corretti, inclusi gli asset.
                        """
                        device = Device(
                            device_id="device-1",
                            standard_id="standard-1",
                            name="Device 1",
                            os="Android",
                            description="Un dispositivo di test",
                            assets=[Asset(
                                asset_id="asset-1",
                                name="Asset 1",
                                asset_type=AssetType.SECURITY,
                                description="Un asset di test"
                            )]
                        )
                        summary_snapshot = device.create_summary_snapshot()
                        assert summary_snapshot.id == "device-1"
                        assert summary_snapshot.standard_id == "standard-1"
                        assert summary_snapshot.name == "Device 1"


                @pytest.mark.requirement("REQ-DEV-01")
                @pytest.mark.priority("high")
                @pytest.mark.type("unità")
                def test_update_asset(self):
                        """
                        Il metodo update_asset aggiorna correttamente i dati di un asset esistente.
                        """
                        device = Device(
                            device_id="device-1",
                            standard_id="standard-1",
                            name="Device 1",
                            os="Android",
                            description="Un dispositivo di test",
                            assets=[Asset(
                                asset_id="asset-1",
                                name="Asset 1",
                                asset_type=AssetType.SECURITY,
                                description="Un asset di test"
                            )]
                        )
                        device.update_asset(asset_id="asset-1", name="Updated Asset", asset_type=AssetType.NETWORK, description="Asset aggiornato")

                        updated_asset = device._get_asset_by_id("asset-1")
                        assert updated_asset.name == "Updated Asset"
                        assert updated_asset.asset_type == AssetType.NETWORK
                        assert updated_asset.description == "Asset aggiornato"



                @pytest.mark.requirement("REQ-DEV-01")
                @pytest.mark.priority("high")
                @pytest.mark.type("unità")

                def test_update_non_existent_asset(self):
                        """
                        Il metodo update_asset solleva un'eccezione se si tenta di aggiornare un asset che non esiste.
                        """
                        device = Device(
                            device_id="device-1",
                            standard_id="standard-1",
                            name="Device 1",
                            os="Android",
                            description="Un dispositivo di test"
                        )
                        with pytest.raises(Exception):
                            device.update_asset(asset_id="non-existent-asset", name="Updated Asset", asset_type=AssetType.NETWORK, description="Asset aggiornato")



                @pytest.mark.requirement("REQ-DEV-01")
                @pytest.mark.priority("high")
                @pytest.mark.type("unità")
                def test_set_node_choice(self):
                        """
                        Il metodo set_node_choice aggiorna correttamente il node choice di un asset.
                        """
                        device = Device(
                            device_id="device-1",
                            standard_id="standard-1",
                            name="Device 1",
                            os="Android",
                            description="Un dispositivo di test",
                        )

                        asset = Asset(
                            asset_id="asset-1",
                            name="Asset 1",
                            asset_type=AssetType.SECURITY,
                            description="Un asset di test",
                            answers=[
                                Answer(requirement_id="req-1", justification="Non applicabile al contesto", node_choices={"node-1": False})
                            ]
                        )
                        
                        device.add_asset(asset)
                        
                        device.set_node_choice(asset_id="asset-1", requirement_id="req-1", node_id="node-1", value=True)
                        
                        asset = device._get_asset_by_id("asset-1")

                        snapshot = asset.create_snapshot()

                        assert snapshot.answers["req-1"].node_choices["node-1"] is True



                @pytest.mark.requirement("REQ-DEV-01")
                @pytest.mark.priority("high")
                @pytest.mark.type("unità")
                def test_create_asset_snapshot(self):
                        """
                        Il metodo create_asset_snapshot restituisce un SnapshotAsset con i dati corretti.
                        """
                        device = Device(
                            device_id="device-1",
                            standard_id="standard-1",
                            name="Device 1",
                            os="Android",
                            description="Un dispositivo di test",
                        )

                        asset = Asset(
                            asset_id="asset-1",
                            name="Asset 1",
                            asset_type=AssetType.SECURITY,
                            description="Un asset di test"
                        )
                        
                        device.add_asset(asset)
                        
                        asset_snapshot = device.create_asset_snapshot("asset-1")
                        
                        assert asset_snapshot.id == "asset-1"
                        assert asset_snapshot.name == "Asset 1"
                        assert asset_snapshot.asset_type == AssetType.SECURITY
                        assert asset_snapshot.description == "Un asset di test"


                @pytest.mark.requirement("REQ-DEV-01")
                @pytest.mark.priority("high")
                @pytest.mark.type("unità")
                def test_create_asset_snapshot_non_existent(self):
                        """
                        Il metodo create_asset_snapshot solleva un'eccezione se si tenta di creare uno snapshot per un asset che non esiste.
                        """
                        device = Device(
                            device_id="device-1",
                            standard_id="standard-1",
                            name="Device 1",
                            os="Android",
                            description="Un dispositivo di test",
                        )
                        with pytest.raises(Exception):
                            device.create_asset_snapshot("non-existent-asset")


                @pytest.mark.requirement("REQ-DEV-01")
                @pytest.mark.priority("high")
                @pytest.mark.type("unità")
                def test_set_justification(self):
                        """
                        Il metodo set_justification aggiorna correttamente la giustificazione di un asset.
                        """
                        device = Device(
                            device_id="device-1",
                            standard_id="standard-1",
                            name="Device 1",
                            os="Android",
                            description="Un dispositivo di test",
                        )

                        asset = Asset(
                            asset_id="asset-1",
                            name="Asset 1",
                            asset_type=AssetType.SECURITY,
                            description="Un asset di test",
                            answers=[
                                 Answer(requirement_id="req-1", justification="Non applicabile al contesto", node_choices={"node-1": False})
                            ]
                        )
                        
                        device.add_asset(asset)
                        
                        device.set_justification(asset_id="asset-1", requirement_id="req-1", justification="Giustificazione aggiornata")
                        
                        asset = device._get_asset_by_id("asset-1")

                        snapshot = asset.create_snapshot()

                        assert snapshot.answers["req-1"].justification == "Giustificazione aggiornata"


                @pytest.mark.requirement("REQ-DEV-01")
                @pytest.mark.priority("high")
                @pytest.mark.type("unità")
                def test_set_justification_non_existent(self):
                        """
                        Il metodo set_justification solleva un'eccezione se si tenta di aggiornare la giustificazione per un asset o requirement che non esiste.
                        """
                        device = Device(
                            device_id="device-1",
                            standard_id="standard-1",
                            name="Device 1",
                            os="Android",
                            description="Un dispositivo di test",
                        )

                        asset = Asset(
                            asset_id="asset-1",
                            name="Asset 1",
                            asset_type=AssetType.SECURITY,
                            description="Un asset di test",
                            answers=[ 
                                 Answer(requirement_id="req-1", justification="Non applicabile al contesto", node_choices={"node-1": False})
                            ]
                        )
                        
                        device.add_asset(asset)
                        
                        with pytest.raises(Exception):
                            device.set_justification(asset_id="asset-1", requirement_id="non-existent-req", justification="Giustificazione aggiornata")



                @pytest.mark.requirement("REQ-DEV-01")
                @pytest.mark.priority("high")
                @pytest.mark.type("unità")
                def test_add_answer(self):
                        """
                        Il metodo add_answer aggiunge correttamente una nuova Answer a un asset.
                        """
                        device = Device(
                            device_id="device-1",
                            standard_id="standard-1",
                            name="Device 1",
                            os="Android",
                            description="Un dispositivo di test",
                        )

                        asset = Asset(
                            asset_id="asset-1",
                            name="Asset 1",
                            asset_type=AssetType.SECURITY,
                            description="Un asset di test",
                            answers=[])
                        
                        device.add_asset(asset)
                        
                        device.add_answer(asset_id="asset-1", answer=Answer(requirement_id="req-1", justification="Non applicabile al contesto", node_choices={"node-1": False}))

                        asset = device._get_asset_by_id("asset-1")

                        snapshot = asset.create_snapshot()

                        assert snapshot.answers["req-1"].requirement_id == "req-1"
                        assert snapshot.answers["req-1"].justification == "Non applicabile al contesto"
                        assert snapshot.answers["req-1"].node_choices["node-1"] is False


                @pytest.mark.requirement("REQ-DEV-01")
                @pytest.mark.priority("high")
                @pytest.mark.type("unità")
                def test_snapshot_immutability(self):
                        """
                        Gli snapshot restituiti dai metodi create_snapshot e create_summary_snapshot sono immutabili.
                        """
                        device = Device(
                            device_id="device-1",
                            standard_id="standard-1",
                            name="Device 1",
                            os="Android",
                            description="Un dispositivo di test",
                            assets=[Asset(
                                asset_id="asset-1",
                                name="Asset 1",
                                asset_type=AssetType.SECURITY,
                                description="Un asset di test"
                            )]
                        )
                        snapshot = device.create_snapshot()
                        summary_snapshot = device.create_summary_snapshot()

                        with pytest.raises(Exception):
                            snapshot.name = "Modified Name"

                        with pytest.raises(Exception):
                            summary_snapshot.name = "Modified Name"