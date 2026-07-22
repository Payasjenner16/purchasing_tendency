import os
from flask import Flask, render_template
from dotenv import load_dotenv

# Load configuration from .env file
load_dotenv()

# Enable local HTTP OAuth transport and relax token scope validation (for development/testing)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

from modules.utils import mail, get_db
from modules.admin import admin_bp
from modules.seller import seller_bp
from modules.buyer import buyer_bp
from modules.auth import auth_bp, google_bp

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "secret123")

# Google OAuth Configuration
app.config["GOOGLE_OAUTH_CLIENT_ID"] = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'projectbased2k26@gmail.com'
app.config['MAIL_PASSWORD'] = 'stsb nann lpnx sskg'
app.config['MAIL_DEFAULT_SENDER'] = 'projectbased2k26@gmail.com'

mail.init_app(app)

# Upload configuration
UPLOAD_FOLDER = "static/uploads/products"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Register blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(seller_bp)
app.register_blueprint(buyer_bp)
app.register_blueprint(google_bp, url_prefix="/login")
app.register_blueprint(auth_bp, url_prefix="/auth")

@app.route("/")
def index():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM products")
    products = cur.fetchall()

    return render_template("index.html", products=products)

if __name__ == "__main__":
    app.run(debug=True)
