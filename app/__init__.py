import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

app = Flask(__name__, instance_relative_config=True)

# Basic config
app.config["SECRET_KEY"] = "dev-secret-key-change-me"
os.makedirs(app.instance_path, exist_ok=True)

db_path = os.path.join(app.instance_path, "perfume_world.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Init extensions
db.init_app(app)

# Import models/routes AFTER app & db are created (important)
from app import models  # noqa: E402,F401
from app import routes  # noqa: E402,F401

# Auto-create tables in dev
with app.app_context():
    db.create_all()