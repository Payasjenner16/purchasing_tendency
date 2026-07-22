from modules.auth import auth_bp, google_bp
from flask import Flask
from flask_dance.contrib.google import make_google_blueprint, google
app = Flask(__name__)

app = Flask(__name__)
app.secret_key = "secret_key"
app.register_blueprint(admin_bp)
app.register_blueprint(seller_bp)
app.register_blueprint(buyer_bp)
@app.route("/")
def home():
    return "Welcome to Purchasing Tendency!"
if __name__ == "__main__":
    app.run(debug=True)
google_bp = make_google_blueprint(
    client_id="131198306016-kveesjhsu9c28os6a3hathamj3phh3ib.apps.googleusercontent.com",
    client_secret="****1HaP",
    redirect_url="/"
)

app.register_blueprint(google_bp, url_prefix="/login")
app.register_blueprint(auth_bp)
app.register_blueprint(google_bp, url_prefix="/login")
@app.route("/")
def index():
    if not google.authorized:
        return '<a href="/login/google">Login with Google</a>'

    response = google.get("/oauth2/v2/userinfo")

    if response.ok:
        user_info = response.json()
        return f"""
        <h2>Welcome {user_info['name']}</h2>
        <p>Email: {user_info['email']}</p>
        """

    return "Failed to get user information"

if __name__ == "__main__":
    app.run(debug=True)
    