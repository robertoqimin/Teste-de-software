from flask import Blueprint, flash, redirect, request, url_for
from werkzeug.security import generate_password_hash

from app.models.site_model import SiteModel
from app.models.user_model import UserModel
from app.views.home_view import render_home


home_blueprint = Blueprint("home", __name__)


@home_blueprint.route("/", methods=["GET", "POST"])
def index():
    site_data = SiteModel().get_home_data()
    user_model = UserModel()
    form_data = {"name": "", "email": ""}

    if request.method == "POST":
        form_data = {
            "name": request.form.get("name", "").strip(),
            "email": request.form.get("email", "").strip(),
        }
        password = request.form.get("password", "")

        if not form_data["name"] or not form_data["email"] or not password:
            flash("Preencha nome, e-mail e senha para realizar o cadastro.", "error")
            return render_home(site_data, form_data)

        if user_model.find_by_email(form_data["email"]):
            flash("Ja existe um usuario cadastrado com este e-mail.", "error")
            return render_home(site_data, form_data)

        password_hash = generate_password_hash(password)
        user_model.create_user(form_data["name"], form_data["email"], password_hash)

        flash("Cadastro realizado com sucesso.", "success")
        return redirect(url_for("home.index"))

    return render_home(site_data, form_data)
