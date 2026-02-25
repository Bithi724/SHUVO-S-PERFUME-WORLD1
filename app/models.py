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
    stock_qty = db.Column(db.Integer, nullable=False, default=0)

    # Men / Women / Unisex
    gender_target = db.Column(db.String(20), nullable=False, default="Unisex")

    # Fresh / Floral / Woody / Oriental / etc.
    category = db.Column(db.String(50), nullable=False, default="General")

    top_notes = db.Column(db.String(200), default="")
    middle_notes = db.Column(db.String(200), default="")
    base_notes = db.Column(db.String(200), default="")

    description = db.Column(db.Text, default="")
    image_url = db.Column(db.String(500), default="")

    is_active = db.Column(db.Boolean, default=True, nullable=False)

    brand_id = db.Column(db.Integer, db.ForeignKey("brand.id"), nullable=False)

    @property
    def stock_label(self):
        if self.stock_qty <= 0:
            return "Out of Stock"
        if self.stock_qty <= 5:
            return f"Low Stock ({self.stock_qty})"
        return f"In Stock ({self.stock_qty})"

    @property
    def stock_class(self):
        if self.stock_qty <= 0:
            return "stock-out"
        if self.stock_qty <= 5:
            return "stock-low"
        return "stock-ok"

    def __repr__(self):
        return f"<Perfume {self.name}>"