from core.domain.session.session_handler import SessionHandler
from core.ports.outbound.evaluation.evaluation_session_exists_port import (
    EvaluationSessionExistPort,
)


class SessionCoordinator:
    def __init__(
        self, exist_port: EvaluationSessionExistPort, session_handler: SessionHandler
    ) -> None:
        self._exist_port = exist_port
        self._session_handler = session_handler

    def can_open_session(self) -> bool:
        """
        Verifica se è possibile aprire una nuova sessione di valutazione.
        Al momento questa classe può essere superflua, ma è necessaria per realizzare l'estensione
        e l'implementazione della sessione legata all'editing del modello.

        Questa classe permette di gestire l'esistenza e le regole di business legate all'apertura di una sessione in un unico punto, facilitando l'estensione futura.

        usa session handler che incapsula la logica di business per decidere se è possibile aprire una nuova sessione, basandosi sull'esistenza di sessioni attive.
        modificandone la firma è possibile estendere la logica di business senza dover modificare il coordinatore, mantenendo il principio di single responsibility.


        Returns:
                bool: True se è possibile aprire una nuova sessione, False altrimenti.
        """

        return self._session_handler.can_open_session(
            self._exist_port.has_active_session()
        )
