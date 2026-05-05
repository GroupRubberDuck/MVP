import os
import string
import random
from flask import Flask
from pymongo import MongoClient
from dotenv import load_dotenv
from .routes import bp

load_dotenv()


def create_app() -> Flask:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, 'backend', 'templates'),
        static_folder=os.path.join(base_dir, 'backend', 'static'),
    )
    app.secret_key = "".join(random.choices(string.ascii_letters + string.digits, k=32))

    db_host = os.environ["DB_HOST"]
    db_port = os.environ["DB_PORT"]
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASSWORD"]
    app.mongodb_client = MongoClient(
        f"mongodb://{db_user}:{db_pass}@{db_host}:{db_port}/",
        serverSelectionTimeoutMS=2000,
    )
    app.db = app.mongodb_client["poc_db"]

    app.register_blueprint(bp)

    return app