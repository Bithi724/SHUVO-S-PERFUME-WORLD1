from app import app, db
from app.models import Brand, Perfume


def pick_model_fields(Model, data: dict) -> dict:
    cols = set(Model.__table__.columns.keys())
    return {k: v for k, v in data.items() if k in cols}


def get_or_create_brand(name: str):
    brand = Brand.query.filter_by(name=name).first()
    if brand:
        return brand

    brand_data = {"name": name}
    brand = Brand(**pick_model_fields(Brand, brand_data))
    db.session.add(brand)
    db.session.flush()  # brand.id পাওয়ার জন্য
    return brand


def add_perfume_if_missing(brand, p: dict):
    existing = Perfume.query.filter_by(name=p["name"], brand_id=brand.id).first()
    if existing:
        return False

    perfume_data = {
        "name": p["name"],
        "price": p["price"],
        "stock_qty": p["stock_qty"],
        "gender_target": p["gender_target"],
        "category": p["category"],
        "top_notes": p["top_notes"],
        "middle_notes": p["middle_notes"],
        "base_notes": p["base_notes"],
        "description": p["description"],
        "image_url": p["image_url"],
        "is_active": True,
        "brand_id": brand.id,
    }

    perfume = Perfume(**pick_model_fields(Perfume, perfume_data))
    db.session.add(perfume)
    return True


def seed():
    with app.app_context():
        # Tables ensure/create
        db.create_all()

        # Brands
        dior = get_or_create_brand("Dior")
        chanel = get_or_create_brand("Chanel")
        armaf = get_or_create_brand("Armaf")
        lattafa = get_or_create_brand("Lattafa")
        versace = get_or_create_brand("Versace")
        zara = get_or_create_brand("Zara")

        perfumes = [
            # Male
            {
                "brand": dior,
                "name": "Sauvage EDT",
                "price": 12500,
                "stock_qty": 12,
                "gender_target": "Male",
                "category": "Fresh",
                "top_notes": "Bergamot, Pepper",
                "middle_notes": "Lavender, Sichuan Pepper",
                "base_notes": "Ambroxan, Cedar",
                "description": "Fresh spicy everyday fragrance with strong projection.",
                "image_url": "",
            },
            {
                "brand": armaf,
                "name": "Club de Nuit Intense Man",
                "price": 4500,
                "stock_qty": 20,
                "gender_target": "Male",
                "category": "Woody",
                "top_notes": "Lemon, Pineapple, Black Currant",
                "middle_notes": "Birch, Jasmine, Rose",
                "base_notes": "Musk, Ambergris, Patchouli",
                "description": "Popular woody-smoky fragrance for evening use.",
                "image_url": "",
            },
            {
                "brand": versace,
                "name": "Eros EDT",
                "price": 8900,
                "stock_qty": 8,
                "gender_target": "Male",
                "category": "Aromatic",
                "top_notes": "Mint, Green Apple, Lemon",
                "middle_notes": "Tonka Bean, Ambroxan",
                "base_notes": "Vanilla, Cedar, Vetiver",
                "description": "Sweet aromatic fragrance, party and night-out friendly.",
                "image_url": "",
            },

            # Female
            {
                "brand": chanel,
                "name": "Coco Mademoiselle EDP",
                "price": 16800,
                "stock_qty": 6,
                "gender_target": "Female",
                "category": "Floral",
                "top_notes": "Orange, Bergamot",
                "middle_notes": "Rose, Jasmine",
                "base_notes": "Patchouli, Vetiver, Vanilla",
                "description": "Elegant floral-citrus perfume for formal and daily wear.",
                "image_url": "",
            },
            {
                "brand": zara,
                "name": "Red Vanilla",
                "price": 2800,
                "stock_qty": 15,
                "gender_target": "Female",
                "category": "Sweet",
                "top_notes": "Black Currant, Pear",
                "middle_notes": "Iris, Vanilla",
                "base_notes": "Praline, Tonka Bean",
                "description": "Budget-friendly sweet fragrance with cozy vanilla profile.",
                "image_url": "",
            },

            # Unisex
            {
                "brand": lattafa,
                "name": "Khamrah",
                "price": 5200,
                "stock_qty": 10,
                "gender_target": "Unisex",
                "category": "Amber",
                "top_notes": "Cinnamon, Nutmeg, Bergamot",
                "middle_notes": "Dates, Praline, Tuberose",
                "base_notes": "Vanilla, Tonka Bean, Benzoin",
                "description": "Warm sweet amber scent, excellent for cooler weather.",
                "image_url": "",
            },
            {
                "brand": lattafa,
                "name": "Asad",
                "price": 3500,
                "stock_qty": 0,
                "gender_target": "Male",
                "category": "Spicy",
                "top_notes": "Black Pepper, Pineapple",
                "middle_notes": "Coffee, Iris, Patchouli",
                "base_notes": "Amber, Vanilla, Dry Woods",
                "description": "Bold spicy profile; currently out of stock for stock filter testing.",
                "image_url": "",
            },
        ]

        added = 0
        for p in perfumes:
            if add_perfume_if_missing(p["brand"], p):
                added += 1

        db.session.commit()
        print(f"Seed completed. Added {added} perfume(s).")
        print("Total perfumes:", Perfume.query.count())


if __name__ == "__main__":
    seed()