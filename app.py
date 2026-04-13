from flask import Flask
from datetime import timedelta
from models import db
from routes import register_store_routes
from admin_routes import register_admin_routes

app = Flask(__name__)
app.secret_key = "skibidi"
app.permanent_session_lifetime = timedelta(hours=24)

# DATABASE CONFIG
DB_HOST = "ecommercewebsite.cho4w6cwgcha.eu-north-1.rds.amazonaws.com"
DB_USER = "PuLSe2106"
DB_NAME = "cosmetz_db"
DB_PORT = "3306"
DB_PASS = "admin2106"

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
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