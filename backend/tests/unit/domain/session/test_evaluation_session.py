import pytest
from unittest.mock import MagicMock

from core.domain.evaluation_object.asset.asset import Asset
from core.domain.evaluation_object.asset.asset_anagraphic import AssetAnagraphic
from core.domain.evaluation_object.asset.asset_proprieties import AssetProprieties
from core.domain.evaluation_object.asset.asset_type import AssetType
from core.domain.evaluation_object.exceptions import AssetNotFoundError
from core.domain.evaluation_object.device import Device
from core.domain.session.evaluation_session import EvaluationSession


def make_asset(asset_id: str = "asset-1") -> Asset:
    return Asset(
        id=asset_id,
        anagraphic=AssetAnagraphic(
            name="Test Asset",
            asset_type=AssetType.NETWORK,
            description="descrizione",
        ),
        proprieties=AssetProprieties(),
    )


def make_session(asset: Asset) -> EvaluationSession:
    device = Device.create(
        device_id="device-1",
        standard_id="std-1",
        name="Device",
        os="Linux",
        description="desc",
        assets=[asset],
    )
    return EvaluationSession(
        session_id="session-1",
        standard=MagicMock(),
        device=device,
    )


class TestInsertJustification:
    def test_justification_viene_salvata(self):
        """
        Dato un asset regolarmente inserito in una sessione di valutazione (Given),
        quando viene impostata una giustificazione testuale per un requisito specifico (When),
        allora il testo deve essere correttamente salvato e rintracciabile nell'evidenza dell'asset (Then).
        """
        asset = make_asset()
        session = make_session(asset)
        testo_giustificazione = "Il dispositivo soddisfa il requisito"

        # Azione: impostiamo la giustificazione
        session.device.get_asset("asset-1").set_justification(
            "req-1", testo_giustificazione
        )

        # Verifica: recuperiamo l'evidenza per controllare se il testo è salvato
        evidence = session.device.get_asset("asset-1").get_evidence("req-1")
        assert evidence is not None
        assert evidence.justification == testo_giustificazione

    def test_justification_vuota_viene_salvata(self):
        """
        Dato un asset all'interno di una sessione (Given),
        quando l'utente inserisce una giustificazione vuota (When),
        allora l'evidenza del requisito deve registrare correttamente la stringa vuota senza sollevare errori (Then).
        """
        asset = make_asset()
        session = make_session(asset)

        # Azione: salviamo una stringa vuota
        session.device.get_asset("asset-1").set_justification("req-1", "")

        # Verifica
        evidence = session.device.get_asset("asset-1").get_evidence("req-1")
        assert evidence.justification == ""

    def test_justification_sovrascrive_precedente(self):
        """
        Data un'evidenza che contiene già una giustificazione salvata (Given),
        quando viene impostata una nuova giustificazione per lo stesso requisito (When),
        allora il sistema deve sovrascrivere il valore precedente con la versione aggiornata (Then).
        """
        asset = make_asset()
        session = make_session(asset)

        # Prima scrittura
        session.device.get_asset("asset-1").set_justification("req-1", "testo vecchio")

        # Seconda scrittura (sovrascrittura)
        session.device.get_asset("asset-1").set_justification(
            "req-1", "versione aggiornata"
        )

        # Verifica
        evidence = session.device.get_asset("asset-1").get_evidence("req-1")
        assert evidence.justification == "versione aggiornata"

    def test_asset_non_trovato_solleva_eccezione(self):
        """
        Data una sessione con un set definito di asset (Given),
        quando si tenta di inserire una giustificazione utilizzando un ID asset non esistente (When),
        allora il dominio deve impedire l'azione sollevando un'eccezione AssetNotFoundError (Then).
        """
        asset = make_asset()
        session = make_session(asset)

        with pytest.raises(AssetNotFoundError):
            session.device.get_asset("asset-inesistente").set_justification(
                "req-1", "testo"
            )
