from flask import Blueprint, render_template
from werkzeug.wrappers import Response

bp = Blueprint("main", __name__)

@bp.route("/")
def hello_world() -> str:
    return "Hello, world!"

@bp.route("/vue")
def hello_world_vue() -> Response:
    return render_template('test_vue.html')