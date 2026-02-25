from flask import render_template, request
from app import app
from app.models import Perfume


@app.route("/", methods=["GET"])
@app.route("/catalog", methods=["GET"])
def home():
    # Query params (filters + sort)
    selected_gender = (request.args.get("gender") or "All").strip()
    selected_category = (request.args.get("category") or "All").strip()
    selected_stock = (request.args.get("stock") or "All").strip()
    selected_sort = (request.args.get("sort") or "Default").strip()

    # Base query
    q = Perfume.query

    # Only active perfumes (if column exists)
    if hasattr(Perfume, "is_active"):
        q = q.filter(Perfume.is_active.is_(True))

    # Gender filter
    if selected_gender.lower() != "all":
        q = q.filter(Perfume.gender_target == selected_gender)

    # Category filter
    if selected_category.lower() != "all":
        q = q.filter(Perfume.category == selected_category)

    # Stock filter (supporting multiple possible dropdown values)
    stock_key = selected_stock.lower().replace("-", " ").replace("_", " ").strip()
    if stock_key in ["in stock", "available", "instock"]:
        q = q.filter(Perfume.stock_qty > 0)
    elif stock_key in ["out of stock", "outofstock"]:
        q = q.filter(Perfume.stock_qty <= 0)
    elif stock_key in ["low stock", "low"]:
        q = q.filter(Perfume.stock_qty > 0, Perfume.stock_qty <= 5)

    # Sorting
    sort_key = selected_sort.lower().replace("-", " ").replace("_", " ").strip()
    if sort_key in ["price low to high", "price asc", "low to high"]:
        q = q.order_by(Perfume.price.asc(), Perfume.id.desc())
    elif sort_key in ["price high to low", "price desc", "high to low"]:
        q = q.order_by(Perfume.price.desc(), Perfume.id.desc())
    elif sort_key in ["name a z", "name asc", "a z"]:
        q = q.order_by(Perfume.name.asc())
    elif sort_key in ["name z a", "name desc", "z a"]:
        q = q.order_by(Perfume.name.desc())
    else:
        # Default = latest first
        q = q.order_by(Perfume.id.desc())

    perfumes = q.limit(50).all()

    # Dropdown options (from DB)
    gender_rows = (
        Perfume.query.with_entities(Perfume.gender_target)
        .distinct()
        .order_by(Perfume.gender_target.asc())
        .all()
    )
    category_rows = (
        Perfume.query.with_entities(Perfume.category)
        .distinct()
        .order_by(Perfume.category.asc())
        .all()
    )

    genders = [row[0] for row in gender_rows if row[0]]
    categories = [row[0] for row in category_rows if row[0]]

    return render_template(
        "home.html",
        perfumes=perfumes,
        genders=genders,
        categories=categories,
        selected_gender=selected_gender,
        selected_category=selected_category,
        selected_stock=selected_stock,
        selected_sort=selected_sort,
        total_found=len(perfumes),
    )


@app.route("/perfume/<int:perfume_id>", methods=["GET"])
def perfume_detail(perfume_id):
    q = Perfume.query

    if hasattr(Perfume, "is_active"):
        q = q.filter(Perfume.is_active.is_(True))

    perfume = q.filter(Perfume.id == perfume_id).first_or_404()

    # Related perfumes (same category if possible)
    related_q = Perfume.query.filter(Perfume.id != perfume.id)

    if hasattr(Perfume, "is_active"):
        related_q = related_q.filter(Perfume.is_active.is_(True))

    if getattr(perfume, "category", None):
        related_q = related_q.filter(Perfume.category == perfume.category)

    related_perfumes = related_q.order_by(Perfume.id.desc()).limit(4).all()

    return render_template(
        "perfume_detail.html",
        perfume=perfume,
        related_perfumes=related_perfumes,
    )