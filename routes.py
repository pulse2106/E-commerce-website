import re
from flask import render_template, request, redirect, url_for, session, flash, jsonify
from sqlalchemy import func
from datetime import datetime
from models import db, User, Product, Comment, Cart, Order, OrderItem

# Define Exchange Rate
EXCHANGE_RATE_INR = 84.0


def register_store_routes(app):

    # --- Currency Context Processor & Route ---
    @app.context_processor
    def utility_processor():
        def format_currency(amount):
            """Converts and formats price based on session currency. Default is INR."""
            if amount is None:
                return "₹0.00"

            try:
                val = float(amount)
            except (ValueError, TypeError):
                return "₹0.00"

            # Default to INR now
            currency = session.get("currency", "INR")

            if currency == "USD":
                # Base is USD
                return f"${val:,.2f}"

            # If INR (Default), convert
            converted = val * EXCHANGE_RATE_INR
            return f"₹{converted:,.2f}"

        return dict(format_currency=format_currency)

    @app.route("/set_currency/<currency_code>")
    def set_currency(currency_code):
        """Route to switch currency and return to previous page."""
        if currency_code in ["USD", "INR"]:
            session["currency"] = currency_code
        return redirect(request.referrer or url_for("home"))

    # ------------------------------------------

    @app.route("/")
    def default():
        return redirect(url_for("home"))

    @app.route("/home")
    def home():
        top_products = (
            Product.query.order_by(Product.access.desc(), Product.id.desc())
            .limit(4)
            .all()
        )
        exclude_ids = [p.id for p in top_products]
        random_products = (
            Product.query.filter(Product.id.notin_(exclude_ids))
            .order_by(func.rand())
            .limit(4)
            .all()
        )
        return render_template(
            "main_page.html", top_products=top_products, random_products=random_products
        )

    @app.route("/login", methods=["POST", "GET"])
    def login():
        next_page = request.args.get("next") or request.form.get("next")
        if request.method == "POST":
            psw = request.form["password"]
            user = request.form["username"]
            find_user = User.query.filter_by(user_name=user).first()
            if find_user and (find_user.pass_word == psw):
                session["username"] = user
                session["is_admin"] = find_user.is_admin
                flash("Login successfully!", "success")
                return redirect(next_page if next_page else url_for("home"))
            flash("Invalid username or password", "error")
        return render_template("login.html", error=False, next_page=next_page)

    @app.route("/register", methods=["POST", "GET"])
    def register():
        if request.method == "POST":
            psw = request.form["password"]
            user = request.form["username"]
            if User.query.filter_by(user_name=user).first():
                return render_template("register.html", error=True)
            new_user = User(user_name=user, pass_word=psw, is_admin=False)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login"))
        return render_template("register.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("Logout successfully!", "info")
        return redirect(url_for("home"))

    @app.route("/category/<category_name>")
    def category(category_name):
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 30, type=int)
        search_query = request.args.get("q", "").strip()
        query = Product.query
        current_currency = session.get("currency", "INR")
        if category_name != "all":
            query = query.filter_by(category=category_name)
        if search_query:
            pattern = r"\b" + re.escape(search_query) + r"\b"
            query = query.filter(Product.product_name.op("REGEXP")(pattern))

        min_p = request.args.get("min_price", type=float)
        max_p = request.args.get("max_price", type=float)
        sort_type = request.args.get("sort", "default")
        selected_subs = request.args.getlist("sub")

        if min_p is not None:
            if current_currency == "INR":
                min_p = min_p / EXCHANGE_RATE_INR
            query = query.filter(Product.price >= min_p)
        if max_p is not None:
            if current_currency == "INR":
                max_p = max_p / EXCHANGE_RATE_INR
            query = query.filter(Product.price <= max_p)
        if selected_subs:
            query = query.filter(Product.subcategory.in_(selected_subs))
        if sort_type == "asc":
            query = query.order_by(Product.price.asc())
        elif sort_type == "desc":
            query = query.order_by(Product.price.desc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        all_subs = (
            db.session.query(Product.subcategory)
            .filter_by(category=category_name)
            .distinct()
            .all()
        )
        subcategories = [s[0] for s in all_subs if s[0]]

        return render_template(
            "category.html",
            products=pagination.items,
            pagination=pagination,
            category_name=category_name,
            search_query=search_query,
            subcategories=subcategories,
            selected_subs=selected_subs,
            min_p=min_p,
            max_p=max_p,
            sort_type=sort_type,
            per_page=per_page,
        )

    @app.route("/product/<int:id>")
    def product(id):
        item = Product.query.get_or_404(id)
        if "viewed_products" not in session:
            session["viewed_products"] = []
        viewed = session["viewed_products"]
        if id not in viewed:
            item.access += 1
            db.session.commit()
            viewed.append(id)
            session["viewed_products"] = viewed
        page = request.args.get("page", 1, type=int)
        pagination = (
            Comment.query.filter_by(product_id=id)
            .order_by(Comment.date_posted.desc())
            .paginate(page=page, per_page=3)
        )
        return render_template(
            "product.html",
            spec=item,
            comments=pagination.items,
            pagination=pagination,
            total_comments=pagination.total,
            category=item.category,
        )

    @app.route("/add-to-cart/<int:product_id>", methods=["POST"])
    def add_to_cart_route(product_id):
        if "username" not in session:
            # Not login
            return redirect(url_for("login", next=url_for("product", id=product_id)))

        user = User.query.filter_by(user_name=session["username"]).first()
        action = request.form.get("action")
        quantity = int(request.form.get("quantity", 1))

        if not user:
            flash("User not found!", "error")
            return redirect(request.referrer or url_for("home"))

        product = Product.query.get(product_id)
        if not product:
            flash("Product not found!", "error")
            return redirect(request.referrer or url_for("home"))

        item = Cart.query.filter_by(user_id=user.id, product_id=product_id).first()

        # Buy and add to cart
        if action == "buy_now":
            if item:
                item.quantity += quantity
                flash(f"{product.product_name} is already in your cart!", "info")
            else:
                new_item = Cart(
                    user_id=user.id, product_id=product_id, quantity=quantity
                )
                db.session.add(new_item)
                flash(f"Added {product.product_name} to cart!", "success")

            db.session.commit()
            return redirect(
                url_for("dashboard", section="cart", product_id=product_id, checked=1)
            )

        else:
            if item:
                item.quantity += quantity
                flash(f"Added {product.product_name} to cart!", "success")
            else:
                new_item = Cart(
                    user_id=user.id, product_id=product_id, quantity=quantity
                )
                db.session.add(new_item)
                flash(f"Added {product.product_name} to cart!", "success")

            db.session.commit()
            return redirect(request.referrer or url_for("product", id=product_id))


    @app.route("/post_comment/<int:id>", methods=["POST"])
    def post_comment(id):
        if "username" not in session:
            return jsonify({"status": "error", "message": "You need to log in first!"}), 401

        content = request.form.get("comment_content")
        if content:
            new_comment = Comment(
                content=content, user_name=session["username"], product_id=id
            )
            db.session.add(new_comment)
            db.session.commit()

            return jsonify(
                {
                    "status": "success",
                    "user_name": new_comment.user_name,
                    "content": new_comment.content,
                    "date": new_comment.date_posted.strftime("%d/%m/%Y %H:%M"),
                }
            )
        return jsonify({"status": "error", "message": "Nothing!"}), 400


    @app.route("/get_comments/<int:product_id>")
    def get_comments(product_id):
        page = request.args.get("page", 1, type=int)

        pagination = (
            Comment.query.filter_by(product_id=product_id)
            .order_by(Comment.date_posted.desc())
            .paginate(page=page, per_page=3)
        )

        comments_html = ""
        for c in pagination.items:
            comments_html += f"""
            <div class="review-card">
                <div class="review-header">
                    <span class="reviewer-name">{c.user_name}</span>
                    <span class="review-date">{c.date_posted.strftime('%d %b %Y')}</span>
                </div>
                <p class="review-body">{c.content}</p>
            </div>
            """

        return jsonify(
            {
                "html": comments_html,
                "current_page": pagination.page,
                "total_pages": pagination.pages,
                "has_prev": pagination.has_prev,
                "has_next": pagination.has_next,
                "prev_num": pagination.prev_num,
                "next_num": pagination.next_num,
            }
        )

    @app.route("/dashboard")
    def dashboard():
        if "username" not in session:
            return redirect(url_for("login"))
        user = User.query.filter_by(user_name=session["username"]).first()
        cart_items = Cart.query.filter_by(user_id=user.id).all()
        orders = (
            Order.query.filter_by(user_id=user.id)
            .order_by(Order.created_at.desc())
            .all()
        )
        checked = request.args.get("checked") == "1"
        now = datetime.utcnow()
        for order in orders:
            time_diff = (now - order.created_at).total_seconds() / 60
            if 15 <= time_diff < 60 and order.status == "PROCESSING":
                order.status = "DELIVERING"
            elif time_diff >= 60 and order.status == "DELIVERING":
                order.status = "ARRIVED"
        db.session.commit()
        return render_template(
            "dashboard_user.html",
            user=user,
            cart_items=(
                Cart.query.filter_by(user_id=user.id).order_by(Cart.id.desc()).all()
            ),
            orders=orders,
            active_orders_count=len([o for o in orders if o.status != "ARRIVED"]),
            comments_count=Comment.query.filter_by(
                user_name=session["username"]
            ).count(),
            cart_items_count=len(cart_items),
            checked=checked,
        )

    @app.route("/update_profile", methods=["POST"])
    def update_profile():
        if "username" not in session:
            return redirect(url_for("login"))

        user = User.query.filter_by(user_name=session["username"]).first()
        if user:
            user.full_name = request.form.get("full_name")
            user.email = request.form.get("email")
            user.phone = request.form.get("phone")
            user.address = request.form.get("address")

            dob = request.form.get("birth_date")
            if dob:
                try:
                    user.birth_date = datetime.strptime(dob, "%Y-%m-%d").date()
                except ValueError:
                    pass

            db.session.commit()
            flash("Profile updated successfully!", "success")

        return redirect(url_for("dashboard"))

    @app.route("/delete-cart-item/<int:item_id>", methods=["POST"])
    def delete_cart_item(item_id):
        item = Cart.query.get(item_id)
        if item:
            db.session.delete(item)
            db.session.commit()
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "Item not found"}), 404


    @app.route("/checkout", methods=["POST"])
    def checkout():
        if "username" not in session:
            return jsonify({"success": False, "message": "You need to log in first!"}), 401

        user = User.query.filter_by(user_name=session["username"]).first()
        if not user:
            return jsonify({"success": False, "message": "User not found!"}), 404

        data = request.get_json()
        cart_item_ids = data.get("cart_item_ids", [])

        if not cart_item_ids:
            return jsonify({"success": False, "message": "No items selected!"}), 400

        cart_items = Cart.query.filter(
            Cart.id.in_(cart_item_ids), Cart.user_id == user.id
        ).all()
        if not cart_items:
            return jsonify({"success": False, "message": "No valid items found!"}), 400

        try:
            total = sum(item.product.price * item.quantity for item in cart_items)
            new_order = Order(user_id=user.id, total_price=total, status="PROCESSING")
            db.session.add(new_order)
            db.session.flush()

            for item in cart_items:
                order_item = OrderItem(
                    order_id=new_order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price_at_purchase=item.product.price,
                )
                db.session.add(order_item)

            Cart.query.filter(Cart.id.in_(cart_item_ids), Cart.user_id == user.id).delete(
                synchronize_session=False
            )

            db.session.commit()

            return jsonify(
                {
                    "success": True,
                    "message": "Order placed successfully! Order #" + str(new_order.id),
                    "order_id": new_order.id,
                }
            )

        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": f"Checkout failed: {str(e)}"}), 500