from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)


class Perfume(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, default=0.0)
    stock_qty = db.Column(db.Integer, default=0)

    gender_target = db.Column(db.String(20), default="Unisex")
    category = db.Column(db.String(50), default="General")

    top_notes = db.Column(db.String(300), default="")
    middle_notes = db.Column(db.String(300), default="")
    base_notes = db.Column(db.String(300), default="")
    description = db.Column(db.Text, default="")

    image_url = db.Column(db.String(500), default="")
    is_active = db.Column(db.Boolean, default=True)

    brand_id = db.Column(db.Integer, db.ForeignKey("brand.id"), nullable=False)
    brand_obj = db.relationship("Brand", backref="perfumes")


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)

    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)