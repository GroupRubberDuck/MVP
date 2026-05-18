import pytest
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
from core.ports.inbound.evaluation.exceptions import (
    OpenEvaluationSessionFailure,
    CommitSessionFailure,
)


class TestCicloValutazione:
    def test_open_session_restituisce_session_id(
        self, evaluation_services, device_adapter, device_with_asset
    ):
        device_adapter.register(device_with_asset)
        session_id = evaluation_services["open"].open_evaluation_session(
            OpenEvaluationSessionCommand(device_id=device_with_asset.id)
        )
        assert isinstance(session_id, str)
        assert len(session_id) > 0

    def test_open_session_doppia(
        self, evaluation_services, device_adapter, device_with_asset
    ):
        device_adapter.register(device_with_asset)
        evaluation_services["open"].open_evaluation_session(
            OpenEvaluationSessionCommand(device_id=device_with_asset.id)
        )
        with pytest.raises(OpenEvaluationSessionFailure):
            evaluation_services["open"].open_evaluation_session(
                OpenEvaluationSessionCommand(device_id=device_with_asset.id)
            )

    def test_open_session_device_inesistente(self, evaluation_services):
        with pytest.raises(OpenEvaluationSessionFailure):
            evaluation_services["open"].open_evaluation_session(
                OpenEvaluationSessionCommand(device_id="device-inesistente")
            )

    def test_evaluate_node(
        self, evaluation_services, device_adapter, device_with_asset
    ):
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
                answer=True,
            )
        )
        session = evaluation_services["cache"].get_evaluation_session(session_id)
        evidence = session.device.get_asset("asset-001").get_evidence("REQ-002")
        assert evidence is not None
        assert evidence.node_choices["N1"] is True

    def test_insert_justification(
        self, evaluation_services, device_adapter, device_with_asset
    ):
        device_adapter.register(device_with_asset)
        session_id = evaluation_services["open"].open_evaluation_session(
            OpenEvaluationSessionCommand(device_id=device_with_asset.id)
        )
        evaluation_services["justification"].insert_justification(
            InsertJustificationCommand(
                session_id=session_id,
                asset_id="asset-001",
                requirement_id="REQ-001",
                justification="Nuova giustificazione dettagliata",
            )
        )
        session = evaluation_services["cache"].get_evaluation_session(session_id)
        evidence = session.device.get_asset("asset-001").get_evidence("REQ-001")
        assert evidence.justification == "Nuova giustificazione dettagliata"

    def test_commit(  # Dopo commit il device in MongoDB contiene le evidenze aggiornate durante la sessione
        self, evaluation_services, device_adapter, device_with_asset
    ):
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
        saved = device_adapter.find_by_id(device_with_asset.id)
        evidence = saved.get_asset("asset-001").get_evidence("REQ-002")
        assert evidence is not None
        assert evidence.node_choices.get("N1") is False

    def test_close_svuota_cache(
        self, evaluation_services, device_adapter, device_with_asset
    ):
        device_adapter.register(device_with_asset)
        session_id = evaluation_services["open"].open_evaluation_session(
            OpenEvaluationSessionCommand(device_id=device_with_asset.id)
        )
        evaluation_services["close"].close_evaluation_session(
            CloseEvaluationSessionCommand(session_id=session_id)
        )
        assert not evaluation_services["cache"].has_active_session()

    def test_commit_session_id_errato(
        self, evaluation_services, device_adapter, device_with_asset
    ):
        device_adapter.register(device_with_asset)
        evaluation_services["open"].open_evaluation_session(
            OpenEvaluationSessionCommand(device_id=device_with_asset.id)
        )
        with pytest.raises(CommitSessionFailure):
            evaluation_services["commit"].commit(
                CommitEvaluationSessionCommand(session_id="session-id-sbagliato")
            )
