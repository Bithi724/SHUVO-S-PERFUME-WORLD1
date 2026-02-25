from flask import Blueprint

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return "<h1>Home route working ✅</h1>"

@main.route("/catalog")
def catalog():
    return "<h1>Catalog route working ✅</h1>"