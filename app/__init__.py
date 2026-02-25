from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "perfume-world-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///perfume_world.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from app.routes import main
    app.register_blueprint(main)

    with app.app_context():
        from app import models
        db.create_all()

    return app