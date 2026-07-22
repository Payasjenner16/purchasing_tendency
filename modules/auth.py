import os
from flask import Blueprint, redirect, url_for, session, flash
from flask_dance.contrib.google import make_google_blueprint, google
from modules.utils import get_db

auth_bp = Blueprint("auth", __name__)

# Google OAuth Blueprint definition.
# It automatically picks up app.config["GOOGLE_OAUTH_CLIENT_ID"] and app.config["GOOGLE_OAUTH_CLIENT_SECRET"]
google_bp = make_google_blueprint(
    scope=["profile", "email"],
    redirect_to="auth.google_login_callback"
)

# Entry point routes to set the target user role before initiating OAuth
@auth_bp.route("/login/buyer")
def login_buyer():
    session["oauth_role"] = "buyer"
    return redirect(url_for("google.login"))

@auth_bp.route("/login/seller")
def login_seller():
    session["oauth_role"] = "seller"
    return redirect(url_for("google.login"))

@auth_bp.route("/login/admin")
def login_admin():
    session["oauth_role"] = "admin"
    return redirect(url_for("google.login"))

@auth_bp.route("/google_login_callback")
def google_login_callback():
    role = session.get("oauth_role", "buyer")
    
    # Mapping for redirection in case of errors
    role_redirects = {
        "buyer": "buyer.buyer_login",
        "seller": "seller.seller_login",
        "admin": "admin.admin"
    }
    
    fallback_redirect = role_redirects.get(role, "buyer.buyer_login")

    if not google.authorized:
        flash("Google login failed.", "danger")
        return redirect(url_for(fallback_redirect))

    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash("Failed to fetch user info from Google.", "danger")
        return redirect(url_for(fallback_redirect))

    user_info = resp.json()
    email = user_info.get("email")
    name = user_info.get("name", "Google User")

    if not email:
        flash("Google account does not share email address.", "danger")
        return redirect(url_for(fallback_redirect))

    conn = get_db()
    cur = conn.cursor()

    if role == "admin":
        # Load authorized administrator emails from environment
        admin_emails_str = os.getenv("ADMIN_EMAILS", "")
        admin_emails = [e.strip().lower() for e in admin_emails_str.split(",") if e.strip()]
        
        # Fallback to the project default mail sender if not configured in .env
        if not admin_emails:
            admin_emails = ["projectbased2k26@gmail.com"]

        if email.lower() in admin_emails:
            session["admin"] = "admin"
            session["admin_email"] = email
            return redirect(url_for("admin.admin_dashboard"))
        else:
            flash("Access denied. Your Google account is not authorized as an administrator.", "danger")
            return redirect(url_for("admin.admin"))

    elif role == "seller":
        cur.execute("SELECT * FROM sellers WHERE email = ?", (email,))
        seller = cur.fetchone()

        if not seller:
            # Auto-register new seller profile
            username = email.split("@")[0]
            cur.execute("SELECT * FROM sellers WHERE username = ?", (username,))
            if cur.fetchone():
                import uuid
                username = f"{username}_{uuid.uuid4().hex[:6]}"

            cur.execute("""
                INSERT INTO sellers (name, email, username, password, status)
                VALUES (?, ?, ?, ?, 'active')
            """, (name, email, username, ""))
            conn.commit()

            # Retrieve newly created seller
            cur.execute("SELECT * FROM sellers WHERE email = ?", (email,))
            seller = cur.fetchone()

        session["seller"] = seller["id"]
        session["seller_name"] = seller["name"]
        session["seller_email"] = seller["email"]
        return redirect(url_for("seller.seller_dashboard"))

    else:  # buyer
        cur.execute("SELECT * FROM buyers WHERE email = ?", (email,))
        buyer = cur.fetchone()

        if not buyer:
            # Auto-register new buyer profile
            username = email.split("@")[0]
            cur.execute("SELECT * FROM buyers WHERE username = ?", (username,))
            if cur.fetchone():
                import uuid
                username = f"{username}_{uuid.uuid4().hex[:6]}"

            cur.execute("""
                INSERT INTO buyers (name, email, username, password)
                VALUES (?, ?, ?, ?)
            """, (name, email, username, ""))
            conn.commit()

            # Retrieve newly created buyer
            cur.execute("SELECT * FROM buyers WHERE email = ?", (email,))
            buyer = cur.fetchone()

        session["buyer"] = buyer["id"]
        session["buyer_name"] = buyer["name"]
        session["buyer_email"] = buyer["email"]
        return redirect(url_for("buyer.buyer_dashboard"))

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")