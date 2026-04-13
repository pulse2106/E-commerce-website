from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), unique=True, nullable=False)
    pass_word = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    full_name = db.Column(db.String(100), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(500), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, user_name, pass_word, email=None, full_name=None, birth_date=None, phone=None, address=None, is_admin=False):
        self.user_name = user_name
        self.pass_word = pass_word
        self.email = email
        self.full_name = full_name
        self.birth_date = birth_date
        self.phone = phone
        self.address = address
        self.is_admin = is_admin

class Product(db.Model):
    __tablename__ = "mytable"
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(256))
    website = db.Column(db.String(50))
    country = db.Column(db.String(50))
    category = db.Column(db.String(50))
    subcategory = db.Column(db.String(50))
    title_href = db.Column("titlehref", db.String(256))
    price = db.Column(db.Float)
    brand = db.Column(db.String(50))
    ingredients = db.Column(db.String(2048))
    form = db.Column(db.String(50))
    tp = db.Column("type", db.String(50))
    color = db.Column(db.String(256))
    size = db.Column(db.String(256))
    rating = db.Column(db.String(50))
    noofratings = db.Column(db.String(50))
    image_url = db.Column(db.String(500))
    access = db.Column(db.Integer, default=0)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_name = db.Column(db.String(100))
    product_id = db.Column(db.Integer, db.ForeignKey("mytable.id"))
    date_posted = db.Column(db.DateTime, default=db.func.now())

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("mytable.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    product = db.relationship("Product")

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    total_price = db.Column(db.Numeric(15, 2), nullable=False)
    status = db.Column(db.String(20), default="Processing")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship("OrderItem", backref="order", lazy=True)

class OrderItem(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("mytable.id"), nullable=False)
    price_at_purchase = db.Column(db.Numeric(15, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    product = db.relationship("Product")