from flask import Blueprint, request, jsonify
from adapters.inbound.flask_controller_interface import FlaskController
from core.ports.inbound.evaluation.evaluation_session.open_evaluation_session_use_case import OpenEvaluationSessionUseCase, OpenEvaluationSessionCommand
from core.ports.inbound.evaluation.evaluation_session.close_evaluation_session_use_case import CloseEvaluationSessionUseCase, CloseEvaluationSessionCommand
from core.ports.inbound.evaluation.evaluation_session.commit_evaluation_session_use_case import CommitEvaluationSessionUseCase, CommitEvaluationSessionCommand
from flask.typing import ResponseReturnValue



class EvaluationSessionController(FlaskController):

    def __init__(
        self,
        open_use_case: OpenEvaluationSessionUseCase,
        close_use_case: CloseEvaluationSessionUseCase,
        commit_use_case: CommitEvaluationSessionUseCase,
    ) -> None:
        self._open = open_use_case
        self._close = close_use_case
        self._commit = commit_use_case


    def register_routes(self,blueprint: Blueprint) -> None:
        blueprint.add_url_rule(
            "/sessions",
            view_func=self.open_session,
            methods=["POST"],
        )
        blueprint.add_url_rule(
            "/sessions/<session_id>",
            view_func=self.close_session,
            methods=["DELETE"],
        )
        blueprint.add_url_rule(
            "/sessions/<session_id>/commit",
            view_func=self.commit_session,
            methods=["POST"],
        )
        blueprint.add_url_rule(
            "/sessions/<session_id>/commit-and-close",
            view_func=self.commit_and_close,
            methods=["POST"],
        )

    def open_session(self) -> ResponseReturnValue:
        body = request.get_json(silent=True) or {}
        command = OpenEvaluationSessionCommand(
            device_id=body.get("device_id", ""),
        )
        session_id = self._open.open_evaluation_session(command)
        return jsonify({"session_id": session_id}), 200

    def close_session(self, session_id: str) -> ResponseReturnValue:
        command = CloseEvaluationSessionCommand(session_id=session_id)
        self._close.close_evaluation_session(command)
        return jsonify({"message": "Sessione chiusa"}), 200

    def commit_session(self, session_id: str) -> ResponseReturnValue:
        command = CommitEvaluationSessionCommand(session_id=session_id)
        self._commit.commit(command)
        return jsonify({"message": "Sessione committata con successo"}), 200

    def commit_and_close(self, session_id: str) -> ResponseReturnValue:
        commit_command = CommitEvaluationSessionCommand(session_id=session_id)
        self._commit.commit(commit_command)

        close_command = CloseEvaluationSessionCommand(session_id=session_id)
        self._close.close_evaluation_session(close_command)

        return jsonify({"message": "Sessione committata e chiusa con successo"}), 200