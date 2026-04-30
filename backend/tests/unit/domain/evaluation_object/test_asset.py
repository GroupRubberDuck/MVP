import pytest
from core.domain.evaluation_object.asset import Asset 
from core.domain.evaluation_object.asset_type import AssetType
from core.domain.evaluation_object.answer import Answer


class TestAsset:
        """Test di creazione della classe Asset"""

        @pytest.mark.requirement("REQ-DEV-01")
        @pytest.mark.priority("high")
        @pytest.mark.type("unità")
        def test_asset_creation(self):
            """
            Un Asset può essere creato solo con id, nome, tipo e descrizione.
            """
            asset = Asset("asset-1", "Asset 1", AssetType.SECURITY, "Descrizione dell'asset")

            assert asset.id == "asset-1"
            assert asset.name == "Asset 1"
            assert asset.asset_type == AssetType.SECURITY
            assert asset.description == "Descrizione dell'asset"
        
        @pytest.mark.requirement("REQ-DEV-01")
        @pytest.mark.priority("high")
        @pytest.mark.type("unità")
        def test_asset_creation_with_answers(self):
            """
            Un Asset può essere creato con un dizionario di Answer iniziale.
            """
            initial_answers = [
                 Answer("acm-1", justification="Non applicabile al contesto", node_choices={"node-1": True}),
                 Answer("acm-2", justification="Conforme allo standard", node_choices={"node-2": False})
            ]
            asset = Asset("asset-1", "Asset 1", AssetType.NETWORK, "Descrizione dell'asset", answers=initial_answers)

            assert asset.id == "asset-1"
            assert asset.name == "Asset 1"
            assert asset.asset_type == AssetType.NETWORK
            assert asset.description == "Descrizione dell'asset"
            assert len(asset._answers) == 2
            assert asset._answers["acm-1"].requirement_id == "acm-1"
            assert asset._answers["acm-1"].justification == "Non applicabile al contesto"
            assert asset._answers["acm-1"].node_choices["node-1"] is True
            assert asset._answers["acm-2"].requirement_id ==        "acm-2"
            assert asset._answers["acm-2"].justification == "Conforme allo standard"
            assert asset._answers["acm-2"].node_choices["node-2"] is False

        
        @pytest.mark.requirement("REQ-DEV-01")
        @pytest.mark.priority("high")
        @pytest.mark.type("unità")
        def test_asset_creation_with_empty_answers(self):
            """
            Un Asset può essere creato con un dizionario vuoto di Answer.
            """
            asset = Asset("asset-1", "Asset 1", AssetType.NETWORK, "Descrizione dell'asset", answers=[])

            assert asset.id == "asset-1"
            assert asset.name == "Asset 1"
            assert asset.asset_type == AssetType.NETWORK
            assert asset.description == "Descrizione dell'asset"
            assert len(asset._answers) == 0
        
        @pytest.mark.requirement("REQ-DEV-01")
        @pytest.mark.priority("high")
        @pytest.mark.type("unità")
        def test_asset_creation_with_none_answers(self):
            """
            Un Asset può essere creato con answers impostato a None.
            """
            asset = Asset("asset-1", "Asset 1", AssetType.NETWORK, "Descrizione dell'asset", answers=None)

            assert asset.id == "asset-1"
            assert asset.name == "Asset 1"
            assert asset.asset_type == AssetType.NETWORK
            assert asset.description == "Descrizione dell'asset"
            assert len(asset._answers) == 0
        
        @pytest.mark.requirement("REQ-DEV-01")
        @pytest.mark.priority("high")
        @pytest.mark.type("unità")
        def test_setter_methods(self):
            """
            I setter di Asset funzionano correttamente.
            """
            asset = Asset("asset-1", "Asset 1", AssetType.SECURITY, "Descrizione dell'asset")
            asset.set_name("Asset 1 Updated")
            asset.set_asset_type(AssetType.NETWORK)
            asset.set_description("Descrizione aggiornata dell'asset")

            assert asset.name == "Asset 1 Updated"
            assert asset.asset_type == AssetType.NETWORK
            assert asset.description == "Descrizione aggiornata dell'asset"

        
        @pytest.mark.requirement("REQ-DEV-01")
        @pytest.mark.priority("high")
        @pytest.mark.type("unità")
        def test_get_answer(self):
            """
            Il metodo _get_answer restituisce l'Answer corretta per un dato requirement_id.
            """
            asset = Asset("asset-1", "Asset 1", AssetType.SECURITY, "Descrizione dell'asset")
            answer = Answer("acm-1", justification="Non applicabile al contesto", node_choices={"node-1": True})
            asset._answers["acm-1"] = answer

            retrieved_answer = asset._get_answer("acm-1")
            assert retrieved_answer is answer
        
        @pytest.mark.requirement("REQ-DEV-01")
        @pytest.mark.priority("high")
        @pytest.mark.type("unità")
        def test_set_node_choice(self):
            """
            Il metodo set_node_choice aggiorna correttamente il node_choice di un'Answer.
            """
            asset = Asset("asset-1", "Asset 1", AssetType.SECURITY, "Descrizione dell'asset")
            answer = Answer("acm-1", justification="Non applicabile al contesto", node_choices={"node-1": True})
            asset._answers["acm-1"] = answer

            asset.set_node_choice("acm-1", "node-1", False)
            assert asset._answers["acm-1"].node_choices["node-1"] is False
        
        @pytest.mark.requirement("REQ-DEV-01")
        @pytest.mark.priority("high")
        @pytest.mark.type("unità")
        def test_set_node_choice_with_invalid_requirement_id(self):
            """
            Il metodo set_node_choice solleva un'eccezione se il requirement_id non esiste.
            """
            asset = Asset("asset-1", "Asset 1", AssetType.SECURITY, "Descrizione dell'asset")

            with pytest.raises(Exception) as exc_info:
                asset.set_node_choice("acm-1", "node-1", True)
            
            assert "Requirement 'acm-1' non trovato" in str(exc_info.value)
        
        @pytest.mark.requirement("REQ-DEV-01")
        @pytest.mark.priority("high")
        @pytest.mark.type("unità")
        def test_set_justification(self):
            """
            Il metodo set_justification aggiorna correttamente la giustificazione di un'Answer.
            """
            asset = Asset("asset-1", "Asset 1", AssetType.SECURITY, "Descrizione dell'asset")
            answer = Answer("acm-1", justification="Non applicabile al contesto", node_choices={"node-1": True})
            asset._answers["acm-1"] = answer

            asset.set_justification("acm-1", "Giustificazione aggiornata")
            assert asset._answers["acm-1"].justification == "Giustificazione aggiornata"
        
        @pytest.mark.requirement("REQ-DEV-01")
        @pytest.mark.priority("high")
        @pytest.mark.type("unità")
        def test_add_answer(self):
                    """Il metodo add_answer aggiunge correttamente una nuova Answer all'Asset."""            
                    asset = Asset("asset-1", "Asset 1", AssetType.SECURITY, "Descrizione dell'asset")
                    answer = Answer("acm-1", justification="Non applicabile al contesto", node_choices={"node-1": True})
                    
                    asset.add_answer(answer)
        
                    assert len(asset._answers) == 1
                    
                    # Confrontiamo gli snapshot: verifica che l'INTERO STATO sia stato copiato correttamente
                    answer_salvata = asset._answers["acm-1"]
                    assert answer_salvata.create_snapshot() == answer.create_snapshot()
                    
                    # (Opzionale) Possiamo anche verificare esplicitamente che le aree di memoria siano diverse
                    assert answer_salvata is not answer

        
        @pytest.mark.requirement("REQ-DEV-01")
        @pytest.mark.priority("high")
        @pytest.mark.type("unità")
        def test_add_answer_with_existing_requirement_id(self):
            """
            Il metodo add_answer solleva un'eccezione se si tenta di aggiungere un'Answer con un requirement_id già esistente.
            """
            asset = Asset("asset-1", "Asset 1", AssetType.SECURITY, "Descrizione dell'asset")
            answer1 = Answer("acm-1", justification="Non applicabile al contesto", node_choices={"node-1": True})
            answer2 = Answer("acm-1", justification="Conforme allo standard", node_choices={"node-2": False})
            asset.add_answer(answer1)

            with pytest.raises(Exception) as exc_info:
                asset.add_answer(answer2)
            
            assert "Impossibile aggiungere: il requisito 'acm-1' esiste già nell'Asset 'Asset 1'." in str(exc_info.value)

        
        @pytest.mark.requirement("REQ-DEV-01")
        @pytest.mark.priority("high")
        @pytest.mark.type("unità")
        def test_create_snapshot(self):
            """
            Il metodo create_snapshot restituisce un AssetSnapshot con i dati corretti.
            """
            asset = Asset("asset-1", "Asset 1", AssetType.SECURITY, "Descrizione dell'asset")
            answer = Answer("acm-1", justification="Non applicabile al contesto", node_choices={"node-1": True})
            asset.add_answer(answer)

            snapshot = asset.create_snapshot()
            assert snapshot.id == "asset-1"
            assert snapshot.name == "Asset 1"
            assert snapshot.asset_type == AssetType.SECURITY
            assert snapshot.description == "Descrizione dell'asset"
            assert snapshot.answers["acm-1"].requirement_id == "acm-1"
            assert snapshot.answers["acm-1"].justification == "Non applicabile al contesto"
            assert snapshot.answers["acm-1"].node_choices["node-1"] is True
        
        @pytest.mark.requirement("REQ-DEV-01")
        @pytest.mark.priority("high")
        @pytest.mark.type("unità")
        def test_create_summary_snapshot(self):
            """
            Il metodo create_summary_snapshot restituisce un AssetSummarySnapshot con i dati corretti.
            """
            asset = Asset("asset-1", "Asset 1", AssetType.SECURITY, "Descrizione dell'asset")
            snapshot = asset.create_summary_snapshot()
            assert snapshot.id == "asset-1"
            assert snapshot.name == "Asset 1"
            assert snapshot.asset_type == AssetType.SECURITY
            assert snapshot.description == "Descrizione dell'asset"
            assert len(snapshot.answers) == 0   
        
        @pytest.mark.requirement("REQ-DEV-01")
        @pytest.mark.priority("high")
        @pytest.mark.type("unità")
        def test_anser_immutability_in_snapshot(self):
            """
            Le Answer restituite nello snapshot di Asset sono immutabili.
            """
            asset = Asset("asset-1", "Asset 1", AssetType.SECURITY, "Descrizione dell'asset")
            answer = Answer("acm-1", justification="Non applicabile al contesto", node_choices={"node-1": True})
            asset.add_answer(answer)

            snapshot = asset.create_snapshot()
            with pytest.raises(Exception):
                snapshot.answers["acm-1"].set_justification("Giustificazione modificata")
            with pytest.raises(Exception):
                snapshot.answers["acm-1"].set_node_choice("node-1", False)      