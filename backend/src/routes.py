from flask import Flask, Blueprint, redirect, url_for, render_template, request
from adapters.inbound.flask_controller_interface import FlaskController


def register_routes(
    app: Flask,
    device_controllers: list[FlaskController] | None = None,
    standard_controllers: list[FlaskController] | None = None,
    evaluation_controllers: list[FlaskController] | None = None,
    report_controllers: list[FlaskController] | None = None,
    asset_controllers: list[FlaskController] | None = None,
) -> None:

    # --- 1. Gestore Globale ID (Context Processor) ---
    # Rende session_id e device_id sempre disponibili nei template Jinja2
    @app.context_processor
    def inject_ids():
        args = request.view_args or {}
        return {
            "session_id": args.get("session_id"),
            "device_id": args.get("device_id"),
        }

    # --- 2. Rotta Principale ---
    @app.route("/")
    def index():
        return redirect(url_for("devices.get_device_list"))

    # --- 3. Registrazione Blueprint ---
    _register_blueprint(app, "devices", device_controllers)
    _register_blueprint(app, "standards", standard_controllers)
    _register_blueprint(app, "evaluation", evaluation_controllers)
    _register_blueprint(app, "report", report_controllers)
    _register_blueprint(app, "assets", asset_controllers)


def _register_blueprint(
    app: Flask,
    name: str,
    controllers: list[FlaskController] | None,
) -> None:
    """Funzione helper per registrare i controller sotto un Blueprint specifico."""
    if not controllers:
        return

    bp = Blueprint(name, __name__)
    for controller in controllers:
        controller.register_routes(bp)
    app.register_blueprint(bp)


def register_error_handlers(app: Flask) -> None:
    """Gestione centralizzata delle pagine di errore (400, 404, 500)."""

    @app.errorhandler(400)
    def bad_request(e):
        return render_template("layouts/errors/400.html", message=str(e)), 400

    @app.errorhandler(404)
    def not_found(e):
        return render_template("layouts/errors/404.html", message=str(e)), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("layouts/errors/500.html", message=str(e)), 500
