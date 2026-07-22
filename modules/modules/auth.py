from flask import Blueprint, redirect, url_for
from flask_dance.contrib.google import make_google_blueprint, google

auth_bp = Blueprint("auth", __name__)

google_bp = make_google_blueprint(
    client_id="PASTE_YOUR_CLIENT_ID",
    client_secret="PASTE_YOUR_CLIENT_SECRET",
    scope=["profile", "email"]
)

@auth_bp.route("/profile")
def profile():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")

    if not resp.ok:
        return "Google login failed"

    user = resp.json()

    return f"""
    <h2>Welcome {user['name']}</h2>
    <p>Email: {user['email']}</p>
    """