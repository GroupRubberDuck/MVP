from flask import Flask, Blueprint, redirect, url_for,render_template
"""
Definisce tutte le rotte dell'applicazione, organizzate in blueprint per modulo funzionale.

Gli if servono a registrare solo i blueprint per cui è stato passato un controller, in modo da poter gestire dinamicamente la disponibilità di funzionalità in base alla configurazione o allo stato dell'applicazione (es. errori di connessione al database).
Permettono di sviluppare e testare più facilmente
Idealmente rimossi al termine dello sviluppo
"""

def register_routes(app: Flask, **controllers) -> None:
    """Registra tutti i blueprint e le rotte globali."""

    # ── Rotta index ──
    @app.route("/")
    def index():
        return redirect(url_for("devices.get_device_list"))

    # ── Blueprint devices ──
    device_bp = Blueprint("devices", __name__)
    if "query_device" in controllers:
        controllers["query_device"].register_routes(device_bp)
    if "import_export_device" in controllers:
        controllers["import_export_device"].register_routes(device_bp)
    app.register_blueprint(device_bp)

    # ── Blueprint compliance standards ──
    if "import_export_standard" in controllers:
        standard_bp = Blueprint("standards", __name__)
        controllers["import_export_standard"].register_routes(standard_bp)
        app.register_blueprint(standard_bp)

    # ── Blueprint evaluation ──
    if "evaluation" in controllers:
        evaluation_bp = Blueprint("evaluation", __name__)
        controllers["evaluation"].register_routes(evaluation_bp)
        app.register_blueprint(evaluation_bp)

    # ── Blueprint report ──
    if "report" in controllers:
        report_bp = Blueprint("report", __name__)
        controllers["report"].register_routes(report_bp)
        app.register_blueprint(report_bp)



def register_error_handlers(app: Flask):

    @app.errorhandler(400)
    def bad_request(e):
        return render_template("layouts/errors/400.html", message=str(e)), 400

    @app.errorhandler(404)
    def not_found(e):
        return render_template("layouts/errors/404.html", message=str(e)), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("layouts/errors/500.html", message=str(e)), 500