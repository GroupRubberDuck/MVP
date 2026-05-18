import pytest
import mongomock
from types import MappingProxyType

from core.domain.evaluation_object.device import Device
from core.domain.evaluation_object.asset.asset import Asset
from core.domain.evaluation_object.asset.asset_anagraphic import AssetAnagraphic
from core.domain.evaluation_object.asset.asset_proprieties import AssetProprieties
from core.domain.evaluation_object.asset.asset_evidence import AssetEvidence
from core.domain.evaluation_object.asset.asset_type import AssetType
from core.domain.evaluation_standard.compliance_standard import ComplianceStandard
from core.domain.evaluation_standard.requirement import Requirement
from core.domain.evaluation_standard.decision_tree import (
    DecisionTree,
    DecisionNode,
    LeafNode,
)
from core.domain.evaluation_standard.standard_verdict import StandardVerdict
from adapters.outbound.device.repository.mongo_device_repository import (
    MongoDeviceAdapter,
)
from adapters.outbound.evaluation.in_memory_evaluation_session_cache import (
    InMemoryEvaluationSessionCache,
)
from adapters.outbound.report.pdf_report_generator import PdfReportGenerator
from core.services.evaluation.evaluation_session.open_evaluation_session_service import (
    OpenEvaluationSessionService,
)
from core.services.evaluation.evaluation_session.close_evaluation_session_service import (
    CloseEvaluationSessionService,
)
from core.services.evaluation.evaluation_session.commit_evaluation_session_service import (
    CommitEvaluationSessionService,
)
from core.services.evaluation.evaluation_session.session_coordinator import (
    SessionCoordinator,
    SessionHandler,
)
from core.services.evaluation.evaluate_decision_node_service import (
    EvaluateDecisionNodeService,
)
from core.services.evaluation.insert_justification_service import (
    InsertJustificationService,
)
from core.services.report.generate_report_service import GenerateReportService


# Database


@pytest.fixture
def mongo_db():
    client = mongomock.MongoClient()
    db = client["test_db"]
    yield db
    client.close()


@pytest.fixture
def device_adapter(mongo_db):
    return MongoDeviceAdapter(mongo_db["devices"])


@pytest.fixture
def session_cache():
    return InMemoryEvaluationSessionCache()


# Dominio


@pytest.fixture
def simple_standard():
    def _tree():
        return DecisionTree(
            root="N1",
            nodes=[
                DecisionNode("N1", "Domanda", "L_PASS", "L_FAIL"),
                LeafNode("L_PASS", StandardVerdict.PASS),
                LeafNode("L_FAIL", StandardVerdict.FAIL),
            ],
        )

    return ComplianceStandard(
        standard_id="STD-001",
        name="Test Standard",
        version_number="1.0",
        requirements=[
            Requirement(
                requirement_id="REQ-001",
                name="Requisito 1",
                description="Desc 1",
                target_description="Target 1",
                decision_tree=_tree(),
                dependency_ids=(),
            ),
            Requirement(
                requirement_id="REQ-002",
                name="Requisito 2",
                description="Desc 2",
                target_description="Target 2",
                decision_tree=_tree(),
                dependency_ids=("REQ-001",),
            ),
        ],
    )


@pytest.fixture
def device_with_asset():
    evidence = AssetEvidence(
        requirement_id="REQ-001",
        node_choices=MappingProxyType({"N1": True}),
        justification="Giustificazione iniziale",
    )
    asset = Asset(
        id="asset-001",
        anagraphic=AssetAnagraphic(
            name="Router",
            asset_type=AssetType.NETWORK,
            description="Router principale",
        ),
        proprieties=AssetProprieties({"REQ-001": evidence}),
    )
    return Device.create(
        device_id="device-001",
        standard_id="STD-001",
        name="Firewall X1",
        os="Linux",
        description="Dispositivo di test",
        assets=[asset],
    )


# Servizi


@pytest.fixture
def evaluation_services(session_cache, device_adapter, simple_standard):
    class FakeStandardRepo:
        def __init__(self, standard):
            self._standard = standard

        def find_standard(self, standard_id: str) -> ComplianceStandard:
            if standard_id == self._standard.id:
                return self._standard
            from core.ports.outbound.compliance_standard.exceptions import (
                StandardNotFoundError,
            )

            raise StandardNotFoundError(f"Standard '{standard_id}' non trovato.")

    coordinator = SessionCoordinator(
        exist_port=session_cache,
        session_handler=SessionHandler(),
    )
    return {
        "open": OpenEvaluationSessionService(
            session_coordinator=coordinator,
            create_session_port=session_cache,
            find_device_port=device_adapter,
            find_standard_port=FakeStandardRepo(simple_standard),
        ),
        "close": CloseEvaluationSessionService(delete_session_port=session_cache),
        "commit": CommitEvaluationSessionService(
            get_evaluation_session_port=session_cache,
            save_device_port=device_adapter,
        ),
        "evaluate_node": EvaluateDecisionNodeService(
            get_evaluation_session_port=session_cache,
            save_evaluation_session_port=session_cache,
        ),
        "justification": InsertJustificationService(
            get_evaluation_session_port=session_cache,
            save_evaluation_session_port=session_cache,
        ),
        "report": GenerateReportService(
            get_evaluation_session_port=session_cache,
            report_generator_port=PdfReportGenerator(),
        ),
        "cache": session_cache,
        "device_adapter": device_adapter,
    }
