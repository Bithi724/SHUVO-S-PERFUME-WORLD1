from flask import render_template, request
from app import app
from app.models import Perfume


@app.route("/")
@app.route("/home")
def home():
    q = Perfume.query

    gender = (request.args.get("gender") or "").strip().lower()
    category = (request.args.get("category") or "").strip()
    stock = (request.args.get("stock") or "").strip().lower()
    sort = (request.args.get("sort") or "").strip().lower()

    if hasattr(Perfume, "is_active"):
        q = q.filter(Perfume.is_active == True)  # noqa: E712

    if gender in {"male", "female", "unisex"} and hasattr(Perfume, "gender_target"):
        q = q.filter(Perfume.gender_target.ilike(gender))

    if category and hasattr(Perfume, "category"):
        q = q.filter(Perfume.category == category)

    if stock == "in" and hasattr(Perfume, "stock_qty"):
        q = q.filter(Perfume.stock_qty > 0)

    if sort == "price_asc" and hasattr(Perfume, "price"):
        q = q.order_by(Perfume.price.asc())
    elif sort == "price_desc" and hasattr(Perfume, "price"):
        q = q.order_by(Perfume.price.desc())
    elif sort == "name_asc" and hasattr(Perfume, "name"):
        q = q.order_by(Perfume.name.asc())
    elif hasattr(Perfume, "id"):
        q = q.order_by(Perfume.id.desc())

    perfumes = q.limit(50).all()

    categories = []
    if hasattr(Perfume, "category"):
        rows = (
            Perfume.query.with_entities(Perfume.category)
            .filter(Perfume.category.isnot(None))
            .distinct()
            .order_by(Perfume.category.asc())
            .all()
        )
        categories = [r[0] for r in rows if r[0]]

    return render_template(
        "home.html",
        perfumes=perfumes,
        categories=categories,
        selected_gender=gender,
        selected_category=category,
        selected_stock=stock,
        selected_sort=sort,
    )