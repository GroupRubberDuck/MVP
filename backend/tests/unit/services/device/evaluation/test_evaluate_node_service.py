import pytest
from unittest.mock import MagicMock

from core.services.evaluation.evaluate_decision_node_service import EvaluateDecisionNodeService
from core.ports.inbound.evaluation.evaluate_decision_node_use_case import EvaluateDecisionNodeCommand
from core.ports.inbound.evaluation.exceptions import EvaluateNodeFailure
from core.ports.outbound.evaluation.exceptions import (
    EvaluationSessionNotFoundError,
    EvaluationSessionSaveError
)
from core.domain.evaluation_object.exceptions import AssetNotFoundError

# --- HELPER FUNCTIONS ---

def make_command(
    session_id="session-1",
    device_id="device-1",
    asset_id="asset-1",
    requirement_id="REQ-1",
    node_id="node-1",
    answer=True
) -> EvaluateDecisionNodeCommand:
    return EvaluateDecisionNodeCommand(
        session_id=session_id,
        device_id=device_id,
        asset_id=asset_id,
        requirement_id=requirement_id,
        node_id=node_id,
        answer=answer
    )

def make_service():
    mock_get_port = MagicMock()
    mock_save_port = MagicMock()
    mock_session = MagicMock()
    mock_asset = MagicMock()

    mock_get_port.get_evaluation_session.return_value = mock_session
    mock_session.device.get_asset.return_value = mock_asset

    service = EvaluateDecisionNodeService(
        get_evaluation_session_port=mock_get_port,
        save_evaluation_session_port=mock_save_port
    )

    return service, mock_get_port, mock_save_port, mock_session, mock_asset


# --- TEST SUITE ---

class TestEvaluateDecisionNodeService:

    def test_evaluate_node_success(self):
        """
        Dato un comando di valutazione nodo valido (Given),
        quando il servizio processa la risposta dell'utente (When),
        allora deve recuperare la sessione e l'asset corretti, aggiornare la scelta del nodo nel dominio e salvare la sessione (Then).
        """
        service, mock_get, mock_save, mock_session, mock_asset = make_service()
        command = make_command()

        service.evaluate_node(command)

        # Ha recuperato la sessione corretta?
        mock_get.get_evaluation_session.assert_called_once_with("session-1")
        # Ha recuperato l'asset corretto?
        mock_session.device.get_asset.assert_called_once_with("asset-1")
        # Ha chiamato set_node_choice con i parametri esatti?
        mock_asset.set_node_choice.assert_called_once_with(
            requirement_id="REQ-1",
            node_id="node-1",
            value=True
        )
        # Ha salvato la sessione modificata?
        mock_save.save_evaluation_session.assert_called_once_with(mock_session)

    def test_solleva_failure_se_sessione_non_trovata(self):
        """
        Dato un ID sessione non presente nella cache (Given),
        quando viene tentata la valutazione di un nodo (When),
        allora il servizio deve sollevare una EvaluateNodeFailure indicando che la sessione non è stata trovata (Then).
        """
        service, mock_get, _, _, _ = make_service()
        mock_get.get_evaluation_session.side_effect = EvaluationSessionNotFoundError("Not found")

        with pytest.raises(EvaluateNodeFailure) as exc_info:
            service.evaluate_node(make_command())

        assert "Sessione 'session-1' non trovata" in str(exc_info.value)

    def test_solleva_failure_se_asset_non_trovato(self):
        """
        Data una sessione valida ma un ID asset non appartenente al dispositivo (Given),
        quando si tenta di impostare una risposta (When),
        allora il servizio deve sollevare una EvaluateNodeFailure riportando l'ID dell'asset mancante (Then).
        """
        service, _, _, mock_session, _ = make_service()
        mock_session.device.get_asset.side_effect = AssetNotFoundError("Not found")

        with pytest.raises(EvaluateNodeFailure) as exc_info:
            service.evaluate_node(make_command())

        assert "Asset 'asset-1' non trovato" in str(exc_info.value)

    def test_solleva_failure_se_dominio_rifiuta_valore(self):
        """
        Dato un nodo o un valore di risposta che viola le regole di validazione del dominio (Given),
        quando l'entità Asset solleva un ValueError (When),
        allora il servizio deve catturare l'eccezione e rilanciare una EvaluateNodeFailure descrittiva (Then).
        """
        service, _, _, _, mock_asset = make_service()
        mock_asset.set_node_choice.side_effect = ValueError("Nodo inesistente")

        with pytest.raises(EvaluateNodeFailure) as exc_info:
            service.evaluate_node(make_command())

        assert "Risposta non valida per il nodo" in str(exc_info.value)

    def test_solleva_failure_se_salvataggio_fallisce(self):
        """
        Dato un errore tecnico durante la persistenza della sessione aggiornata (Given),
        quando il servizio tenta di salvare lo stato (When),
        allora deve sollevare una EvaluateNodeFailure per notificare il fallimento dell'operazione (Then).
        """
        service, _, mock_save, _, _ = make_service()
        mock_save.save_evaluation_session.side_effect = EvaluationSessionSaveError("DB Disconnesso")

        with pytest.raises(EvaluateNodeFailure) as exc_info:
            service.evaluate_node(make_command())

        assert "Errore durante il salvataggio" in str(exc_info.value)