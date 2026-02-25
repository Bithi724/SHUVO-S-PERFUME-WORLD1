from app import db

class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    perfumes = db.relationship("Perfume", backref="brand_obj", lazy=True)

    def __repr__(self):
        return f"<Brand {self.name}>"


class Perfume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.0)
    gender = db.Column(db.String(20), default="Unisex")  # Men/Women/Unisex
    top_notes = db.Column(db.String(200))
    middle_notes = db.Column(db.String(200))
    base_notes = db.Column(db.String(200))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    brand_id = db.Column(db.Integer, db.ForeignKey("brand.id"), nullable=False)

    def __repr__(self):
        return f"<Perfume {self.name}>"