import pytest

from core.domain.evaluation_engine.evaluation_detail import (
    AssetEvaluationDetail,
    DeviceEvaluationDetail,
    RequirementEvaluationDetail,
)
from core.domain.evaluation_standard.evaluation_state import EvaluationState

from adapters.outbound.report.pdf_report_generator import PdfReportGenerator


@pytest.fixture
def adapter():
    return PdfReportGenerator()


@pytest.fixture
def sample_device_detail():
    req_pass = RequirementEvaluationDetail(
        requirement_id="REQ-01",
        name="Controllo Password",
        description="Verifica complessità password",
        target="Il sistema deve forzare password complesse",
        justification="",
        node_choices={"n1": True},
        nodes=[],
        state=EvaluationState.PASS,
        dependencies=[],
    )

    req_fail = RequirementEvaluationDetail(
        requirement_id="REQ-02",
        name="Crittografia Disco",
        description="Verifica crittografia storage",
        target="I dati a riposo devono essere cifrati",
        justification="Il disco primario non è cifrato con BitLocker.",
        node_choices={"n1": False},
        nodes=[],
        state=EvaluationState.FAIL,
        dependencies=[],
    )

    asset = AssetEvaluationDetail(
        asset_id="ASSET-123",
        name="Database Server",
        asset_type="Server",
        description="Server Linux principale",
        requirement_details=(req_pass, req_fail),
        verdict=EvaluationState.FAIL,
    )

    return DeviceEvaluationDetail(
        device_id="DEV-001",
        name="Infrastruttura Core",
        operating_system="Ubuntu 22.04",
        description="Ambiente di produzione",
        standard_id="ISO-27001",
        asset_details=(asset,),
        verdict=EvaluationState.FAIL,
    )


@pytest.fixture
def empty_device_detail():
    """Un dispositivo senza alcun asset, per testare i casi limite."""
    return DeviceEvaluationDetail(
        device_id="DEV-002",
        name="Dispositivo Vuoto",
        operating_system="Windows",
        description="Nessun asset configurato",
        standard_id="NIST",
        asset_details=tuple(),
        verdict=EvaluationState.NA,
    )


class TestPdfReportGeneratorAdapter:
    def test_generate_returns_valid_pdf_bytes_with_data(
        self, adapter, sample_device_detail
    ):
        stream = adapter.generate_report(sample_device_detail)
        result = stream.read()

        assert isinstance(result, bytes)
        assert len(result) > 0
        assert result.startswith(b"%PDF-")

    def test_generate_handles_empty_assets_gracefully(
        self, adapter, empty_device_detail
    ):
        stream = adapter.generate_report(empty_device_detail)
        result = stream.read()

        assert isinstance(result, bytes)
        assert result.startswith(b"%PDF-")

    def test_all_evaluation_states_are_supported(self, adapter):
        reqs = [
            RequirementEvaluationDetail(
                requirement_id=f"REQ-{state.name}",
                name="Test",
                description="Test",
                target="Test",
                justification="Test",
                node_choices={},
                nodes=[],
                state=state,
                dependencies=[],
            )
            for state in EvaluationState
        ]

        asset = AssetEvaluationDetail(
            asset_id="A1",
            name="A1",
            asset_type="T1",
            description="D1",
            requirement_details=tuple(reqs),
            verdict=EvaluationState.PENDING,
        )

        device = DeviceEvaluationDetail(
            device_id="D1",
            name="D1",
            operating_system="OS",
            description="D",
            standard_id="STD",
            asset_details=(asset,),
            verdict=EvaluationState.PENDING,
        )

        stream = adapter.generate_report(device)
        result = stream.read()

        assert result.startswith(b"%PDF-")
