from flask import Flask, Blueprint, redirect, url_for, render_template
from adapters.inbound.flask_controller_interface import FlaskController


def register_routes(
    app: Flask,
    device_controllers: list[FlaskController] | None = None,
    standard_controllers: list[FlaskController] | None = None,
    evaluation_controllers: list[FlaskController] | None = None,
    report_controllers: list[FlaskController] | None = None,
    asset_controllers: list[FlaskController] | None = None, 
) -> None:

    # --- Rotte Root ---
    @app.route("/")
    def index():
        return redirect(url_for("devices.get_device_list"))

    # --- Rotte UI (User Interface) ---
    # Queste rotte servono solo a caricare il template HTML che contiene il codice Vue
    
    @app.route("/sessions/<session_id>/devices/<device_id>/assets/create")
    def create_asset_page(session_id, device_id):
        return render_template(
            "layouts/asset/create_asset.html", 
            session_id=session_id, 
            device_id=device_id, 
            asset=None
        )

    @app.route("/sessions/<session_id>/devices/<device_id>/assets/<asset_id>/edit")
    def edit_asset_page(session_id, device_id, asset_id):
        # Passiamo un dizionario minimo per far capire a Vue che siamo in modalità edit
        return render_template(
            "layouts/asset/create_asset.html", 
            session_id=session_id, 
            device_id=device_id, 
            asset={"asset_id": asset_id}
        )

    # --- Registrazione Blueprint (API e Logica) ---
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
    if not controllers:
        return
    bp = Blueprint(name, __name__)
    for controller in controllers:
        controller.register_routes(bp)
    app.register_blueprint(bp)


def register_error_handlers(app: Flask) -> None:

    @app.errorhandler(400)
    def bad_request(e):
        return render_template("layouts/errors/400.html", message=str(e)), 400

    @app.errorhandler(404)
    def not_found(e):
        return render_template("layouts/errors/404.html", message=str(e)), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("layouts/errors/500.html", message=str(e)), 500