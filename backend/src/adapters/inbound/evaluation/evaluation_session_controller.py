from flask import Blueprint, Response, request, jsonify

from core.ports.inbound.evaluation.evaluation_session.open_evaluation_session_use_case import OpenEvaluationSessionUseCase, OpenEvaluationSessionCommand
from core.ports.inbound.evaluation.evaluation_session.close_evaluation_session_use_case import CloseEvaluationSessionUseCase, CloseEvaluationSessionCommand
from core.ports.inbound.evaluation.evaluation_session.save_evaluation_session_use_case import SaveEvaluationSessionUseCase, SaveEvaluationSessionCommand
from core.ports.inbound.evaluation.evaluation_session.commit_evaluation_session_use_case import CommitEvaluationSessionUseCase, CommitEvaluationSessionCommand

evaluation_session_blueprint = Blueprint("evaluation_session", __name__)


class EvaluationSessionController:

    def __init__(
        self,
        open_use_case: OpenEvaluationSessionUseCase,
        close_use_case: CloseEvaluationSessionUseCase,
        save_use_case: SaveEvaluationSessionUseCase,
        commit_use_case: CommitEvaluationSessionUseCase,
    ) -> None:
        self._open = open_use_case
        self._close = close_use_case
        self._save = save_use_case
        self._commit = commit_use_case
        self._register_routes()

    def _register_routes(self) -> None:
        evaluation_session_blueprint.add_url_rule(
            "/sessions",
            view_func=self.open_session,
            methods=["POST"],
        )
        evaluation_session_blueprint.add_url_rule(
            "/sessions/<session_id>",
            view_func=self.close_session,
            methods=["DELETE"],
        )
        evaluation_session_blueprint.add_url_rule(
            "/sessions/<session_id>",
            view_func=self.save_session,
            methods=["PUT"],
        )
        evaluation_session_blueprint.add_url_rule(
            "/sessions/<session_id>/commit",
            view_func=self.commit_session,
            methods=["POST"],
        )
        evaluation_session_blueprint.add_url_rule(
            "/sessions/<session_id>/commit-and-close",
            view_func=self.commit_and_close,
            methods=["POST"],
        )

    def open_session(self) -> Response:
        body = request.get_json(silent=True) or {}
        command = OpenEvaluationSessionCommand(
            device_id=body.get("device_id", ""),
            session_id=body.get("session_id", ""),
        )
        session_id = self._open.open(command)
        return jsonify({"session_id": session_id}), 201

    def close_session(self, session_id: str) -> Response:
        command = CloseEvaluationSessionCommand(session_id=session_id)
        self._close.close_evaluation_session(command)
        return jsonify({"message": "Sessione chiusa"}), 200

    def save_session(self, session_id: str) -> Response:
        command = SaveEvaluationSessionCommand(session_id=session_id)
        self._save.save(command)
        return jsonify({"message": "Sessione salvata con successo"}), 200

    def commit_session(self, session_id: str) -> Response:
        command = CommitEvaluationSessionCommand(session_id=session_id)
        self._commit.commit(command)
        return jsonify({"message": "Sessione committata con successo"}), 200

    def commit_and_close(self, session_id: str) -> Response:
        commit_command = CommitEvaluationSessionCommand(session_id=session_id)
        self._commit.commit(commit_command)

        close_command = CloseEvaluationSessionCommand(session_id=session_id)
        self._close.close_evaluation_session(close_command)

        return jsonify({"message": "Sessione committata e chiusa con successo"}), 200