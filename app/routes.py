from flask import render_template, request, redirect, url_for
from app import app, db
from app.models import Perfume, Brand


# =========================
# PUBLIC: HOME / CATALOG
# =========================
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

    q = Perfume.query

    # active filter (safe)
    if hasattr(Perfume, "is_active"):
        q = q.filter(Perfume.is_active.is_(True))

    # search (name)
    if selected_search:
        q = q.filter(Perfume.name.ilike(f"%{selected_search}%"))

    # brand filter (brand id)
    if selected_brand != "All":
        try:
            q = q.filter(Perfume.brand_id == int(selected_brand))
        except ValueError:
            pass

    # gender filter
    if selected_gender != "All":
        q = q.filter(Perfume.gender_target == selected_gender)

    # category filter
    if selected_category != "All":
        q = q.filter(Perfume.category == selected_category)

    # stock filter
    if selected_stock == "In Stock":
        q = q.filter(Perfume.stock_qty > 0)
    elif selected_stock == "Low Stock":
        q = q.filter(Perfume.stock_qty > 0, Perfume.stock_qty <= 5)
    elif selected_stock == "Out of Stock":
        q = q.filter(Perfume.stock_qty <= 0)

    # sorting
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
        perfumes=perfumes,
        brands=brands,
        genders=genders,
        categories=categories,
        selected_search=selected_search,
        selected_brand=selected_brand,
        selected_gender=selected_gender,
        selected_category=selected_category,
        selected_stock=selected_stock,
        selected_sort=selected_sort,
        total_found=total_found,
        page=page,
        total_pages=total_pages,
        per_page=per_page,
    )


# =========================
# PUBLIC: DETAIL
# =========================
@app.route("/perfume/<int:perfume_id>", methods=["GET"])
def perfume_detail(perfume_id):
    q = Perfume.query
    if hasattr(Perfume, "is_active"):
        q = q.filter(Perfume.is_active.is_(True))

    perfume = q.filter(Perfume.id == perfume_id).first_or_404()

    related_q = Perfume.query.filter(Perfume.id != perfume.id)
    if hasattr(Perfume, "is_active"):
        related_q = related_q.filter(Perfume.is_active.is_(True))
    if perfume.category:
        related_q = related_q.filter(Perfume.category == perfume.category)

    related_perfumes = related_q.order_by(Perfume.id.desc()).limit(4).all()

    return render_template("perfume_detail.html", perfume=perfume, related_perfumes=related_perfumes)


# =========================
# ADMIN: SHORTCUT
# =========================
@app.route("/admin", methods=["GET"])
def admin_home():
    return redirect(url_for("admin_perfumes"))


# =========================
# ADMIN: LIST (EDIT/DELETE here)
# =========================
@app.route("/admin/perfumes", methods=["GET"])
def admin_perfumes():
    perfumes = Perfume.query.order_by(Perfume.id.desc()).all()
    return render_template("admin_perfumes.html", perfumes=perfumes)


# =========================
# ADMIN: ADD (NEW)
# =========================
@app.route("/admin/perfumes/new", methods=["GET", "POST"])
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

        brand_id_raw = (request.form.get("brand_id") or "").strip()
        new_brand_name = (request.form.get("new_brand_name") or "").strip()

        is_active_checked = ("is_active" in request.form)

        if not name:
            error_msg = "Perfume name is required."

        try:
            price = float(price_raw)
        except ValueError:
            error_msg = "Price must be a number."
            price = 0.0

        try:
            stock_qty = int(stock_raw)
        except ValueError:
            error_msg = "Stock qty must be an integer."
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
                error_msg = "Select a brand or add a new brand."

        if not error_msg:
            perfume = Perfume(
                name=name,
                price=price,
                stock_qty=stock_qty,
                gender_target=gender_target,
                category=category,
                top_notes=top_notes,
                middle_notes=middle_notes,
                base_notes=base_notes,
                description=description,
                image_url=image_url,
                brand_id=brand_obj.id,
            )
            # is_active only if exists in model
            if hasattr(perfume, "is_active"):
                perfume.is_active = is_active_checked

            db.session.add(perfume)
            db.session.commit()
            return redirect(url_for("admin_perfumes"))

    return render_template("admin_add_perfume.html", brands=brands, error_msg=error_msg)


# =========================
# ADMIN: EDIT
# =========================
@app.route("/admin/perfumes/<int:perfume_id>/edit", methods=["GET", "POST"])
def admin_edit_perfume(perfume_id):
    perfume = db.session.get(Perfume, perfume_id)
    if not perfume:
        return "Perfume not found", 404

    brands = Brand.query.order_by(Brand.name.asc()).all()
    error_msg = ""

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        if not name:
            error_msg = "Name is required."
        else:
            perfume.name = name
            perfume.gender_target = (request.form.get("gender_target") or "Unisex").strip()
            perfume.category = (request.form.get("category") or "General").strip()
            perfume.top_notes = (request.form.get("top_notes") or "").strip()
            perfume.middle_notes = (request.form.get("middle_notes") or "").strip()
            perfume.base_notes = (request.form.get("base_notes") or "").strip()
            perfume.description = (request.form.get("description") or "").strip()
            perfume.image_url = (request.form.get("image_url") or "").strip()

            if hasattr(perfume, "is_active"):
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


# =========================
# ADMIN: DELETE
# =========================
@app.route("/admin/perfumes/<int:perfume_id>/delete", methods=["POST"])
def admin_delete_perfume(perfume_id):
    perfume = db.session.get(Perfume, perfume_id)
    if not perfume:
        return "Perfume not found", 404
    db.session.delete(perfume)
    db.session.commit()
    return redirect(url_for("admin_perfumes"))