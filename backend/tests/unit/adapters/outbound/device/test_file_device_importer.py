import io
import pytest

from adapters.outbound.device.importer.file_device_importer import FileDeviceImporter
from core.domain.evaluation_object.asset.asset_type import AssetType
from core.ports.outbound.device.exceptions import (
    InvalidAssetTypeError,
    MissingDeviceFieldError,
    FileTooLargeError
)


class _StubImporter(FileDeviceImporter):
    def __init__(self, data: dict):
        self._data = data

    def _pre_validate(self, content) -> None:
        pass

    def _deserialize(self, content) -> dict:
        return self._data

    def _parse_data(self, raw) -> dict:
        return raw


def _full_data(**overrides) -> dict:
    base = {
        "device_id": "DEV-001",
        "standard_id": "STD-001",
        "name": "Router",
        "os": "Linux",
        "description": "Test",
        "assets": [],
    }
    base.update(overrides)
    return base


def _asset_data(**overrides) -> dict:
    base = {
        "id": "ASSET-001",
        "name": "WiFi",
        "asset_type": "network",
        "description": "desc",
        "evaluations": [],
    }
    base.update(overrides)
    return base


class TestBuildDevice:

    def test_builds_device_with_correct_fields(self):
        """
        Dati i campi obbligatori device_id, standard_id, name e os deserializzati correttamente da un file (Given),
        quando il metodo parse_device_file costruisce l'oggetto Device a partire dai dati grezzi (When),
        allora tutte le proprietà principali del dispositivo devono corrispondere esattamente ai valori forniti in input (Then).
        """
        device = _StubImporter(_full_data()).parse_device_file(io.BytesIO())
        assert device.id == "DEV-001"
        assert device.standard_id == "STD-001"
        assert device.name == "Router"
        assert device.os == "Linux"

    def test_builds_device_without_assets(self):
        """
        Dato un set di dati dispositivo in cui la lista degli asset è esplicitamente vuota (Given),
        quando l'importer completa la costruzione dell'oggetto Device (When),
        allora la collezione degli asset del dispositivo deve risultare vuota, senza elementi inattesi (Then).
        """
        device = _StubImporter(_full_data()).parse_device_file(io.BytesIO())
        assert len(device.assets) == 0

    def test_builds_device_with_assets(self):
        """
        Dati due asset distinti con ID 'A1' e 'A2' associati al dispositivo nei dati deserializzati (Given),
        quando l'importer assembla l'oggetto Device completo (When),
        allora entrambi gli asset devono essere presenti nella collezione, accessibili tramite i rispettivi ID (Then).
        """
        data = _full_data(assets=[_asset_data(id="A1"), _asset_data(id="A2")])
        device = _StubImporter(data).parse_device_file(io.BytesIO())
        assert len(device.assets) == 2
        assert "A1" in device.assets

    def test_raises_missing_field_when_device_id_empty(self):
        """
        Dati deserializzati in cui il campo obbligatorio device_id è una stringa vuota (Given),
        quando l'importer tenta di costruire il dispositivo e convalidare i campi (When),
        allora deve sollevare un'eccezione MissingDeviceFieldError per segnalare l'assenza del valore richiesto (Then).
        """
        with pytest.raises(MissingDeviceFieldError):
            _StubImporter(_full_data(device_id="")).parse_device_file(io.BytesIO())

    def test_raises_missing_field_when_standard_id_empty(self):
        """
        Dati deserializzati in cui il campo obbligatorio standard_id risulta assente o vuoto (Given),
        quando la validazione dei campi del dispositivo viene eseguita durante il parsing (When),
        allora l'importer deve bloccare l'operazione sollevando un'eccezione MissingDeviceFieldError (Then).
        """
        with pytest.raises(MissingDeviceFieldError):
            _StubImporter(_full_data(standard_id="")).parse_device_file(io.BytesIO())

    def test_raises_missing_field_when_name_empty(self):
        """
        Dati deserializzati in cui il nome del dispositivo, campo obbligatorio, è una stringa vuota (Given),
        quando l'importer esegue il controllo di validità prima di restituire il Device (When),
        allora deve sollevare MissingDeviceFieldError per impedire la creazione di un dispositivo incompleto (Then).
        """
        with pytest.raises(MissingDeviceFieldError):
            _StubImporter(_full_data(name="")).parse_device_file(io.BytesIO())


class TestBuildAsset:

    def test_builds_asset_with_correct_type(self):
        """
        Dato un asset il cui asset_type nei dati grezzi è la stringa 'security' (Given),
        quando l'importer costruisce l'oggetto Asset e mappa il tipo testuale nell'enum corrispondente (When),
        allora la proprietà asset_type dell'anagrafica deve risultare esattamente AssetType.SECURITY (Then).
        """
        data = _full_data(assets=[_asset_data(asset_type="security")])
        device = _StubImporter(data).parse_device_file(io.BytesIO())
        assert device.assets["ASSET-001"].anagraphic.asset_type == AssetType.SECURITY

    def test_builds_asset_with_evidence(self):
        """
        Dato un asset che include una evaluation con requirement_id, evaluation_map e justification valorizzati (Given),
        quando l'importer deserializza e associa l'evidenza all'asset corrispondente (When),
        allora l'evidenza recuperata tramite get_evidence deve contenere le scelte dei nodi e la giustificazione coerenti con i dati forniti (Then).
        """
        evaluation = {
            "requirement_id": "REQ-1",
            "evaluation_map": {"N1": True},
            "justification": "ok",
        }
        data = _full_data(assets=[_asset_data(evaluations=[evaluation])])
        device = _StubImporter(data).parse_device_file(io.BytesIO())
        evidence = device.assets["ASSET-001"].get_evidence("REQ-1")
        assert evidence is not None
        assert evidence.node_choices["N1"] is True
        assert evidence.justification == "ok"

    def test_builds_asset_without_evaluations(self):
        """
        Dato un asset la cui lista di evaluations è esplicitamente vuota nei dati deserializzati (Given),
        quando viene richiesta un'evidenza per un requirement non presente (When),
        allora il metodo get_evidence deve restituire None, indicando l'assenza di valutazioni registrate per quell'asset (Then).
        """
        data = _full_data(assets=[_asset_data(evaluations=[])])
        device = _StubImporter(data).parse_device_file(io.BytesIO())
        assert device.assets["ASSET-001"].get_evidence("REQ-1") is None

    def test_raises_invalid_asset_type_on_unknown_value(self):
        """
        Dato un asset il cui asset_type nei dati grezzi contiene un valore non riconosciuto ('unknown') (Given),
        quando l'importer tenta di mappare la stringa nell'enum AssetType (When),
        allora deve sollevare un'eccezione InvalidAssetTypeError per segnalare che il tipo non è supportato (Then).
        """
        data = _full_data(assets=[_asset_data(asset_type="unknown")])
        with pytest.raises(InvalidAssetTypeError):
            _StubImporter(data).parse_device_file(io.BytesIO())

class TestPreValidate:

    class _SizeCheckStub(FileDeviceImporter):

        def _deserialize(self, content) -> dict:
            return {}
        def _parse_data(self, raw) -> dict:
            return raw

    @pytest.fixture
    def importer(self):
        return self._SizeCheckStub()

    def test_raises_file_too_large_error_when_size_exceeds_limit(self, importer):
        """
        Dato un flusso di byte la cui dimensione supera il limite massimo consentito di 10 MB anche di un solo byte (Given),
        quando l'importer esegue la validazione preliminare (_pre_validate) prima del parsing (When),
        allora deve immediatamente sollevare un'eccezione FileTooLargeError per rifiutare il file sovradimensionato (Then).
        """
        content = io.BytesIO(b"x" * (10 * 1024 * 1024 + 1))
        with pytest.raises(FileTooLargeError):
            importer.parse_device_file(content)

    def test_accepts_file_exactly_at_size_limit(self, importer):
        """
        Dato un flusso di byte la cui dimensione è esattamente pari al limite massimo di 10 MB (Given),
        quando l'importer esegue il pre-validazione sulla dimensione del file (When),
        allora il controllo deve essere superato senza sollevare FileTooLargeError, consentendo la prosecuzione del parsing (Then).
        """
        content = io.BytesIO(b"x" * (10 * 1024 * 1024))
        with pytest.raises(Exception) as exc_info:
            importer.parse_device_file(content)
        assert not isinstance(exc_info.value, FileTooLargeError)