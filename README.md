# E-commerce Website

Flask-based e-commerce application with customer browsing, cart, comments, order tracking, and an admin dashboard.

## Project Structure

- `app.py` starts the Flask app, configures the database, and registers the route groups.
- `models.py` defines the SQLAlchemy models for users, products, comments, cart items, orders, and order items.
- `routes.py` contains the storefront routes for login, registration, home page, category browsing, product pages, cart actions, currency switching, and comments.
- `admin_routes.py` contains the admin dashboard, order management, customer management, and product management routes.
- `templates/` contains the HTML pages rendered by Flask.
- `static/` contains CSS, JavaScript, images, and other frontend assets.
- `Sequels.sql` is the database schema dump.

## Main Features

- User registration and login
- Product browsing by category and subcategory
- Search, sorting, pagination, and price filtering
- Product detail pages with comments
- Cart add/buy-now flow
- Admin-only dashboard with charts and management pages
- Currency display toggle between USD and INR

## Requirements

Install the dependencies with:

```bash
pip install -r requirements.txt
```

## Setup

1. Create and activate a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Configure your MySQL database connection in `app.py`.
4. Import the schema from `Sequels.sql` if you want to preload the tables and sample data.
5. Start the application with `python app.py`.

By default, the app runs in debug mode and listens on `http://127.0.0.1:5000/`.

## Running the App

```bash
python app.py
```

On startup, the app initializes SQLAlchemy and calls `db.create_all()` before launching the Flask development server.

## Code Overview

### `app.py`

Creates the Flask application, sets the session lifetime, configures the database connection, initializes SQLAlchemy, and registers the route modules.

### `models.py`

Defines the data model used by the site:

- `User`
- `Product`
- `Comment`
- `Cart`
- `Order`
- `OrderItem`

### `routes.py`

Handles the customer-facing experience:

- `/home`
- `/login`
- `/register`
- `/logout`
- `/category/<category_name>`
- `/product/<id>`
- `/add-to-cart/<product_id>`
- `/post_comment/<id>`
- `/set_currency/<currency_code>`

### `admin_routes.py`

Handles admin-only pages:

- `/admin/dashboard`
- `/admin/orders`
- `/admin/products`
- `/admin/customers`
- `/admin/customer/toggle_admin/<user_id>`

## Notes

- The database credentials are currently hardcoded in `app.py`. Replace them with your own values before deploying or sharing the project.
- The application uses MySQL with `mysql-connector-python` and SQLAlchemy.
- Admin access is checked through the session state, so create or mark at least one admin user in the database before using the admin pages.
