from flask import Flask
from datetime import timedelta
from dotenv import load_dotenv
import os
from models import db
from routes import register_store_routes
from admin_routes import register_admin_routes

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-only-secret-key")
app.permanent_session_lifetime = timedelta(hours=24)

# DATABASE CONFIG
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_NAME = os.getenv("DB_NAME", "cosmetz_db")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_PASS = os.getenv("DB_PASS", "")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299

# Initialize DB
db.init_app(app)

# Register Routes
register_store_routes(app)
register_admin_routes(app)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
