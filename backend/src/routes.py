from flask import Blueprint, render_template

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return "<h1>Backend attivo</h1><p><a href='/test-vue'>Vai al trrrrrest Vue</a></p>"


@bp.route("/test-vue")
def test_vue():
    return render_template("test_vue.html")
