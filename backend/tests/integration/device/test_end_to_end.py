# Flusso completo con formato JSON:
# 1. Salva device in DB
# 2. Sessione di valutazione (open → evaluate → justify → commit → close)
# 3. Esporta il device aggiornato in JSON
# 4. Re-importa da JSON
# 5. Verifica che node_choices e justification siano intatti

from core.ports.inbound.evaluation.evaluation_session.open_evaluation_session_use_case import (
    OpenEvaluationSessionCommand,
)
from core.ports.inbound.evaluation.evaluation_session.close_evaluation_session_use_case import (
    CloseEvaluationSessionCommand,
)
from core.ports.inbound.evaluation.evaluation_session.commit_evaluation_session_use_case import (
    CommitEvaluationSessionCommand,
)
from core.ports.inbound.evaluation.evaluate_decision_node_use_case import (
    EvaluateDecisionNodeCommand,
)
from core.ports.inbound.evaluation.insert_justification_use_case import (
    InsertJustificationCommand,
)
from adapters.outbound.device.exporter.json_file_device_exporter import (
    JSONFileDeviceExporter,
)
from adapters.outbound.device.importer.json_file_device_importer import (
    JSONFileDeviceImporter,
)
from adapters.outbound.device.exporter.xml_file_device_exporter import (
    XMLFileDeviceExporter,
)
from adapters.outbound.device.importer.xml_file_device_importer import (
    XMLFileDeviceImporter,
)


class TestRoundTripEndToEnd:
    def _esegui_sessione_completa(self, evaluation_services, device_id, asset_id):
        session_id = evaluation_services["open"].open_evaluation_session(
            OpenEvaluationSessionCommand(device_id=device_id)
        )
        evaluation_services["evaluate_node"].evaluate_node(
            EvaluateDecisionNodeCommand(
                session_id=session_id,
                device_id=device_id,
                asset_id=asset_id,
                requirement_id="REQ-001",
                node_id="N1",
                answer=True,
            )
        )
        evaluation_services["evaluate_node"].evaluate_node(
            EvaluateDecisionNodeCommand(
                session_id=session_id,
                device_id=device_id,
                asset_id=asset_id,
                requirement_id="REQ-002",
                node_id="N1",
                answer=True,
            )
        )
        evaluation_services["justification"].insert_justification(
            InsertJustificationCommand(
                session_id=session_id,
                asset_id=asset_id,
                requirement_id="REQ-001",
                justification="Giustificazione aggiornata nel round-trip",
            )
        )
        evaluation_services["commit"].commit(
            CommitEvaluationSessionCommand(session_id=session_id)
        )
        evaluation_services["close"].close_evaluation_session(
            CloseEvaluationSessionCommand(session_id=session_id)
        )
        return session_id

    def test_json_export_reimport_preserva_evidenze(
        self, evaluation_services, device_adapter, device_with_asset
    ):
        device_adapter.register(device_with_asset)
        self._esegui_sessione_completa(
            evaluation_services,
            device_id=device_with_asset.id,
            asset_id="asset-001",
        )
        # Export
        saved = device_adapter.find_by_id(device_with_asset.id)
        stream = JSONFileDeviceExporter().generate_device_file(saved)
        stream.seek(0)
        # Re-import
        reimported = JSONFileDeviceImporter().parse_device_file(stream)

        assert reimported.id == device_with_asset.id
        ev_001 = reimported.get_asset("asset-001").get_evidence("REQ-001")
        assert ev_001 is not None
        assert ev_001.node_choices["N1"] is True
        assert ev_001.justification == "Giustificazione aggiornata nel round-trip"
        ev_002 = reimported.get_asset("asset-001").get_evidence("REQ-002")
        assert ev_002 is not None
        assert ev_002.node_choices["N1"] is True

    def test_xml_export_reimport_preserva_evidenze(
        self, evaluation_services, device_adapter, device_with_asset
    ):

        # Flusso completo con formato XML:

        device_adapter.register(device_with_asset)
        session_id = evaluation_services["open"].open_evaluation_session(
            OpenEvaluationSessionCommand(device_id=device_with_asset.id)
        )
        evaluation_services["evaluate_node"].evaluate_node(
            EvaluateDecisionNodeCommand(
                session_id=session_id,
                device_id=device_with_asset.id,
                asset_id="asset-001",
                requirement_id="REQ-002",
                node_id="N1",
                answer=False,
            )
        )
        evaluation_services["commit"].commit(
            CommitEvaluationSessionCommand(session_id=session_id)
        )
        evaluation_services["close"].close_evaluation_session(
            CloseEvaluationSessionCommand(session_id=session_id)
        )
        # Export XML
        saved = device_adapter.find_by_id(device_with_asset.id)
        stream = XMLFileDeviceExporter().generate_device_file(saved)
        stream.seek(0)
        # Re-import XML
        reimported = XMLFileDeviceImporter().parse_device_file(stream)

        ev = reimported.get_asset("asset-001").get_evidence("REQ-002")
        assert ev is not None
        assert ev.node_choices["N1"] is False

    def test_cache_vuota_dopo_round_trip_completo(
        self, evaluation_services, device_adapter, device_with_asset
    ):

        device_adapter.register(device_with_asset)
        self._esegui_sessione_completa(
            evaluation_services,
            device_id=device_with_asset.id,
            asset_id="asset-001",
        )
        assert not evaluation_services["cache"].has_active_session()


# forse serve un flusso completo anche in CVS?
