import json
import pandas as pd
import plotly.express as px
import plotly.utils
from flask import render_template, request, redirect, url_for, session, flash
from sqlalchemy import func
from models import db, User, Product, Order

EXCHANGE_RATE_INR = 84.0


def register_admin_routes(app):
    @app.before_request
    def restrict_admin_access():
        """Ensure only admins can access /admin routes."""
        if request.path.startswith("/admin"):
            if "username" not in session or not session.get("is_admin"):
                flash("Unauthorized access!", "error")
                return redirect(url_for("login"))

    @app.route("/admin/dashboard")
    def admin_dashboard():
        """Main Admin Overview with Plotly charts."""
        total_revenue = db.session.query(func.sum(Order.total_price)).scalar() or 0
        total_orders = db.session.query(func.count(Order.id)).scalar() or 0
        total_users = db.session.query(func.count(User.id)).scalar() or 0

        # Currency
        currency = session.get("currency", "INR")
        rate = 1.0
        currency_prefix = "$"
        if currency == "INR":
            rate = EXCHANGE_RATE_INR
            currency_prefix = "₹"

        # Revenue Trend Chart
        revenue_query = db.session.query(Order.created_at, Order.total_price).order_by(
            Order.created_at
        )
        df_revenue = pd.read_sql(revenue_query.statement, db.session.connection())
        chart_revenue = None
        if not df_revenue.empty:
            df_revenue["total_price"] = df_revenue["total_price"] * rate

            df_revenue["date"] = pd.to_datetime(df_revenue["created_at"]).dt.date
            df_daily = df_revenue.groupby("date")["total_price"].sum().reset_index()

            fig_rev = px.line(df_daily, x="date", y="total_price", markers=True)
            fig_rev.update_traces(line_color="#D4A373")
            fig_rev.update_layout(yaxis_tickprefix=currency_prefix)

            chart_revenue = fig_rev.to_json()

        # Order Status Pie Chart
        status_query = db.session.query(
            Order.status, func.count(Order.id).label("count")
        ).group_by(Order.status)

        # Get raw results and manually construct dataframe
        status_results = status_query.all()
        # Create with native Python types, not numpy
        status_data = [(str(row[0]), int(row[1])) for row in status_results]
        df_status = pd.DataFrame(status_data, columns=["Status", "Count"])

        chart_status = None
        if not df_status.empty:
            fig_status = px.pie(df_status, values="Count", names="Status", hole=0.4)

            # Convert to dict and ensure values are plain JSON
            fig_dict = fig_status.to_dict()

            # Explicitly convert binary encoded values back to plain numbers
            if fig_dict.get("data") and len(fig_dict["data"]) > 0:
                trace = fig_dict["data"][0]
                # Replace binary encoded data with plain JSON
                if "y" in trace:
                    trace["y"] = df_status["Count"].tolist()
                if "values" in trace:
                    trace["values"] = df_status["Count"].tolist()

            chart_status = json.dumps(fig_dict, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template(
            "admin_dashboard.html",
            revenue=total_revenue,
            orders=total_orders,
            users=total_users,
            chart_revenue=chart_revenue,
            chart_status=chart_status,
        )

    @app.route("/admin/orders")
    def admin_orders():
        """Displays orders with optional ID search."""
        search_query = request.args.get("search_query", "").strip()
        query = Order.query

        if search_query and search_query.isdigit():
            query = query.filter_by(id=int(search_query))
        elif search_query:
            query = query.filter(Order.id == None)

        orders = query.order_by(Order.created_at.desc()).all()
        return render_template("admin_orders.html", orders=orders)

    @app.route("/admin/products")
    def admin_products():
        """Paginated product inventory with ID search."""
        page = request.args.get("page", 1, type=int)
        search_query = request.args.get("search_query", "").strip()

        query = Product.query

        if search_query and search_query.isdigit():
            query = query.filter_by(id=int(search_query))
        elif search_query:
            query = query.filter(Product.id == None)

        pagination = query.order_by(Product.id.desc()).paginate(page=page, per_page=20)
        return render_template(
            "admin_products.html", products=pagination.items, pagination=pagination
        )

    @app.route("/admin/customers")
    def admin_customers():
        """User directory with ID search."""
        search_query = request.args.get("search_query", "").strip()
        query = User.query

        if search_query and search_query.isdigit():
            query = query.filter_by(id=int(search_query))
        elif search_query:
            query = query.filter(User.id == None)

        customers = query.order_by(User.id.desc()).all()
        return render_template("admin_customers.html", customers=customers)

    @app.route("/admin/customer/toggle_admin/<int:user_id>", methods=["POST"])
    def toggle_admin_status(user_id):
        """Toggle the admin status of a user."""
        user = User.query.get_or_404(user_id)

        # Prevent an admin from revoking their own status
        if session.get("username") == user.user_name:
            flash("You cannot revoke your own admin status.", "error")
            return redirect(url_for("admin_customers"))

        user.is_admin = not user.is_admin
        db.session.commit()

        status = "Admin" if user.is_admin else "User"
        flash(f"User {user.user_name} is now an {status}.", "success")
        return redirect(url_for("admin_customers"))
