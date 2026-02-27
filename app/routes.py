from functools import wraps
from flask import render_template, request, redirect, url_for, session
from app import app, db
from app.models import Perfume, Brand, User


def _safe_next(u: str) -> str:
    if u and u.startswith("/") and "://" not in u:
        return u
    return url_for("home")


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login", next=request.path))
        return fn(*args, **kwargs)
    return wrapper


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login", next=request.path))
        if not session.get("is_admin"):
            return "Forbidden (Admin only)", 403
        return fn(*args, **kwargs)
    return wrapper


# -------------------------
# AUTH (User + Admin same login)
# -------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if session.get("user_id"):
        return redirect(url_for("home"))

    err = ""
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        email = (request.form.get("email") or "").strip()
        password = (request.form.get("password") or "").strip()
        confirm = (request.form.get("confirm") or "").strip()

        if not username or not password:
            err = "Username এবং Password লাগবে।"
        elif password != confirm:
            err = "Password match করছে না।"
        elif User.query.filter_by(username=username).first():
            err = "এই username আগে থেকেই আছে।"
        elif email and User.query.filter_by(email=email).first():
            err = "এই email আগে থেকেই আছে।"
        else:
            u = User(username=username, email=email if email else None, is_admin=False)
            u.set_password(password)
            db.session.add(u)
            db.session.commit()
            return redirect(url_for("login"))

    return render_template("signup.html", error_msg=err)


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("home"))

    err = ""
    next_url = _safe_next(request.args.get("next") or "")

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = (request.form.get("password") or "").strip()
        next_url = _safe_next(request.form.get("next") or "")

        u = User.query.filter_by(username=username).first()
        if u and u.check_password(password):
            session["user_id"] = u.id
            session["username"] = u.username
            session["is_admin"] = bool(u.is_admin)
            return redirect(next_url or url_for("home"))

        err = "Wrong username/password."

    return render_template("login.html", error_msg=err, next_url=next_url)


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    session.pop("is_admin", None)
    return redirect(url_for("home"))


@app.route("/admin")
def admin_shortcut():
    return redirect(url_for("admin_perfumes"))


# -------------------------
# PUBLIC: Catalog + Detail
# -------------------------
@app.route("/", methods=["GET"])
@app.route("/catalog", methods=["GET"])
def home():
    selected_search = (request.args.get("q") or "").strip()
    selected_brand = (request.args.get("brand") or "All").strip()
    selected_gender = (request.args.get("gender") or "All").strip()
    selected_category = (request.args.get("category") or "All").strip()
    selected_stock = (request.args.get("stock") or "All").strip()
    selected_sort = (request.args.get("sort") or "Default").strip()

    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1
    page = max(page, 1)
    per_page = 6

    q = Perfume.query.filter(Perfume.is_active.is_(True))

    if selected_search:
        q = q.filter(Perfume.name.ilike(f"%{selected_search}%"))

    if selected_brand != "All":
        try:
            q = q.filter(Perfume.brand_id == int(selected_brand))
        except ValueError:
            pass

    if selected_gender != "All":
        q = q.filter(Perfume.gender_target == selected_gender)

    if selected_category != "All":
        q = q.filter(Perfume.category == selected_category)

    if selected_stock == "In Stock":
        q = q.filter(Perfume.stock_qty > 0)
    elif selected_stock == "Low Stock":
        q = q.filter(Perfume.stock_qty > 0, Perfume.stock_qty <= 5)
    elif selected_stock == "Out of Stock":
        q = q.filter(Perfume.stock_qty <= 0)

    if selected_sort == "Name A Z":
        q = q.order_by(Perfume.name.asc())
    elif selected_sort == "Name Z A":
        q = q.order_by(Perfume.name.desc())
    elif selected_sort == "Price Low to High":
        q = q.order_by(Perfume.price.asc(), Perfume.id.desc())
    elif selected_sort == "Price High to Low":
        q = q.order_by(Perfume.price.desc(), Perfume.id.desc())
    else:
        q = q.order_by(Perfume.id.desc())

    total_found = q.count()
    total_pages = (total_found + per_page - 1) // per_page if total_found else 1
    page = min(page, total_pages)
    perfumes = q.offset((page - 1) * per_page).limit(per_page).all()

    brands = Brand.query.order_by(Brand.name.asc()).all()
    genders = [r[0] for r in Perfume.query.with_entities(Perfume.gender_target).distinct().all() if r[0]]
    categories = [r[0] for r in Perfume.query.with_entities(Perfume.category).distinct().all() if r[0]]

    return render_template(
        "home.html",
        perfumes=perfumes, brands=brands, genders=genders, categories=categories,
        selected_search=selected_search, selected_brand=selected_brand,
        selected_gender=selected_gender, selected_category=selected_category,
        selected_stock=selected_stock, selected_sort=selected_sort,
        total_found=total_found, page=page, total_pages=total_pages, per_page=per_page
    )


@app.route("/perfume/<int:perfume_id>")
def perfume_detail(perfume_id):
    perfume = Perfume.query.filter_by(id=perfume_id, is_active=True).first_or_404()
    related = Perfume.query.filter(
        Perfume.id != perfume.id,
        Perfume.is_active.is_(True),
        Perfume.category == perfume.category
    ).order_by(Perfume.id.desc()).limit(4).all()
    return render_template("perfume_detail.html", perfume=perfume, related_perfumes=related)


# -------------------------
# ADMIN: Manage (Admin only)
# -------------------------
@app.route("/admin/perfumes")
@admin_required
def admin_perfumes():
    perfumes = Perfume.query.order_by(Perfume.id.desc()).all()
    return render_template("admin_perfumes.html", perfumes=perfumes)


@app.route("/admin/perfumes/new", methods=["GET", "POST"])
@admin_required
def admin_add_perfume():
    error_msg = ""
    brands = Brand.query.order_by(Brand.name.asc()).all()

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        price_raw = (request.form.get("price") or "0").strip()
        stock_raw = (request.form.get("stock_qty") or "0").strip()
        gender_target = (request.form.get("gender_target") or "Unisex").strip()
        category = (request.form.get("category") or "General").strip()
        top_notes = (request.form.get("top_notes") or "").strip()
        middle_notes = (request.form.get("middle_notes") or "").strip()
        base_notes = (request.form.get("base_notes") or "").strip()
        description = (request.form.get("description") or "").strip()
        image_url = (request.form.get("image_url") or "").strip()
        is_active = ("is_active" in request.form)

        brand_id_raw = (request.form.get("brand_id") or "").strip()
        new_brand_name = (request.form.get("new_brand_name") or "").strip()

        if not name:
            error_msg = "Perfume name required."

        try:
            price = float(price_raw)
        except ValueError:
            error_msg = "Price must be a number."
            price = 0.0

        try:
            stock_qty = int(stock_raw)
        except ValueError:
            error_msg = "Stock must be an integer."
            stock_qty = 0

        brand_obj = None
        if not error_msg:
            if new_brand_name:
                brand_obj = Brand.query.filter_by(name=new_brand_name).first()
                if not brand_obj:
                    brand_obj = Brand(name=new_brand_name)
                    db.session.add(brand_obj)
                    db.session.flush()
            elif brand_id_raw:
                try:
                    brand_obj = db.session.get(Brand, int(brand_id_raw))
                except ValueError:
                    brand_obj = None

            if not brand_obj:
                error_msg = "Select brand or add new brand."

        if not error_msg:
            p = Perfume(
                name=name, price=price, stock_qty=stock_qty,
                gender_target=gender_target, category=category,
                top_notes=top_notes, middle_notes=middle_notes, base_notes=base_notes,
                description=description, image_url=image_url,
                is_active=is_active, brand_id=brand_obj.id
            )
            db.session.add(p)
            db.session.commit()
            return redirect(url_for("admin_perfumes"))

    return render_template("admin_add_perfume.html", brands=brands, error_msg=error_msg)


@app.route("/admin/perfumes/<int:perfume_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_perfume(perfume_id):
    perfume = db.session.get(Perfume, perfume_id)
    if not perfume:
        return "Not found", 404

    brands = Brand.query.order_by(Brand.name.asc()).all()
    error_msg = ""

    if request.method == "POST":
        perfume.name = (request.form.get("name") or "").strip()
        perfume.gender_target = (request.form.get("gender_target") or "Unisex").strip()
        perfume.category = (request.form.get("category") or "General").strip()
        perfume.top_notes = (request.form.get("top_notes") or "").strip()
        perfume.middle_notes = (request.form.get("middle_notes") or "").strip()
        perfume.base_notes = (request.form.get("base_notes") or "").strip()
        perfume.description = (request.form.get("description") or "").strip()
        perfume.image_url = (request.form.get("image_url") or "").strip()
        perfume.is_active = ("is_active" in request.form)

        try:
            perfume.price = float((request.form.get("price") or "0").strip())
        except ValueError:
            error_msg = "Price must be a number."

        try:
            perfume.stock_qty = int((request.form.get("stock_qty") or "0").strip())
        except ValueError:
            error_msg = "Stock must be an integer."

        bid = (request.form.get("brand_id") or "").strip()
        if bid:
            try:
                perfume.brand_id = int(bid)
            except ValueError:
                pass

        if not error_msg:
            db.session.commit()
            return redirect(url_for("admin_perfumes"))

    return render_template("admin_edit_perfume.html", perfume=perfume, brands=brands, error_msg=error_msg)


@app.route("/admin/perfumes/<int:perfume_id>/delete", methods=["POST"])
@admin_required
def admin_delete_perfume(perfume_id):
    perfume = db.session.get(Perfume, perfume_id)
    if not perfume:
        return "Not found", 404
    db.session.delete(perfume)
    db.session.commit()
    return redirect(url_for("admin_perfumes"))