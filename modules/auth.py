from modules.auth import auth_bp, google_bp
from flask import Blueprint, redirect, url_for, session
from flask_dance.contrib.google import make_google_blueprint, google

auth_bp = Blueprint("auth", __name__)

google_bp = make_google_blueprint(
    client_id="131198306016-kveesjhsu9c28os6a3hathamj3phh3ib.apps.googleusercontent.com",
    client_secgoogle_bp = make_google_blueprint(
    # client_id="paste_your_client_id_here",
    client_secret="paste_your_client_secret_here",
    scope=["profile", "email"]
)ret="YOUR_GOOGLE_CLIENT_SECRET",
    scope=[
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid"
    ]
)

@auth_bp.route("/profile")
def profile():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")

    if not resp.ok:
        return "Failed to fetch user information"

    user_info = resp.json()

    return f"""
    <h2>Welcome {user_info['name']}</h2>
    <p>Email: {user_info['email']}</p>
    <img src="{user_info['picture']}" width="100">
    """

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")