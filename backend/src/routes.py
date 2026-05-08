from flask import Flask, Blueprint, redirect, url_for, render_template
from adapters.inbound.flask_controller_interface import FlaskController


def register_routes(
    app: Flask,
    device_controllers: list[FlaskController] | None = None,
    standard_controllers: list[FlaskController] | None = None,
    evaluation_controllers: list[FlaskController] | None = None,
    report_controllers: list[FlaskController] | None = None,
) -> None:

    @app.route("/")
    def index():
        return redirect(url_for("devices.get_device_list"))

    _register_blueprint(app, "devices", device_controllers)
    _register_blueprint(app, "standards", standard_controllers)
    _register_blueprint(app, "evaluation", evaluation_controllers)
    _register_blueprint(app, "report", report_controllers)


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