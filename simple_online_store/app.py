from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple

from flask import (
    Flask,
    render_template,
    session,
    redirect,
    url_for,
    request,
    flash,
)


app = Flask(__name__)

# NOTE: In a real application, keep this secret key out of source control.
app.secret_key = "dev-secret-change-me"


@dataclass
class Product:
    id: int
    name: str
    price: float
    category: str
    description: str
    image_url: str
    badge: str | None = None


# In-memory product catalog for the prototype
PRODUCTS: List[Product] = [
    Product(
        id=1,
        name="Aurora Wireless Headphones",
        price=129.99,
        category="Audio",
        description=(
            "Immerse yourself in crystal-clear sound with active noise cancellation, "
            "30-hour battery life, and ultra-soft ear cushions."
        ),
        image_url="https://images.pexels.com/photos/3394664/pexels-photo-3394664.jpeg?auto=compress&cs=tinysrgb&w=800",
        badge="Best Seller",
    ),
    Product(
        id=2,
        name="Lumen Smart Lamp",
        price=79.0,
        category="Smart Home",
        description=(
            "A minimalist smart lamp with adaptive color temperature, "
            "voice assistant integration, and customizable scenes."
        ),
        image_url="https://images.pexels.com/photos/112811/pexels-photo-112811.jpeg?auto=compress&cs=tinysrgb&w=800",
        badge="New",
    ),
    Product(
        id=3,
        name="Nebula Mechanical Keyboard",
        price=149.5,
        category="Accessories",
        description=(
            "A compact mechanical keyboard with hot-swappable switches, "
            "per-key RGB, and a premium aluminum frame."
        ),
        image_url="https://images.pexels.com/photos/160107/pexels-photo-160107.jpeg?auto=compress&cs=tinysrgb&w=800",
        badge="Limited",
    ),
    Product(
        id=4,
        name="Pulse Fitness Tracker",
        price=59.99,
        category="Wearables",
        description=(
            "Track your heart rate, sleep, and workouts with a 7-day battery life "
            "and water-resistant design."
        ),
        image_url="https://images.pexels.com/photos/4049943/pexels-photo-4049943.jpeg?auto=compress&cs=tinysrgb&w=800",
    ),
    Product(
        id=5,
        name="Echo Studio Speakers",
        price=219.0,
        category="Audio",
        description=(
            "Studio-grade speakers with deep bass, room-filling sound, and multi-room "
            "synchronization."
        ),
        image_url="https://images.pexels.com/photos/696291/pexels-photo-696291.jpeg?auto=compress&cs=tinysrgb&w=800",
    ),
    Product(
        id=6,
        name="Orbit Drone Mini",
        price=99.99,
        category="Gadgets",
        description=(
            "A palm-sized drone with 4K camera, gesture controls, and auto-stabilization "
            "for smooth footage."
        ),
        image_url="https://images.pexels.com/photos/163792/drone-dji-phantom-quadrocopter-163792.jpeg?auto=compress&cs=tinysrgb&w=800",
    ),
]


def get_product(product_id: int) -> Product | None:
    for product in PRODUCTS:
        if product.id == product_id:
            return product
    return None


def get_cart() -> Dict[str, int]:
    """
    Retrieve the cart from the session, ensuring a consistent structure.

    Cart structure:
        {
            "<product_id>": quantity,
            ...
        }
    """
    cart = session.get("cart")
    if cart is None:
        cart = {}
        session["cart"] = cart
    return cart


def cart_items_and_totals() -> Tuple[List[Dict], float]:
    cart = get_cart()
    items: List[Dict] = []
    subtotal = 0.0

    for product_id_str, quantity in cart.items():
        try:
            product_id = int(product_id_str)
        except (TypeError, ValueError):
            continue

        product = get_product(product_id)
        if not product:
            continue

        line_total = product.price * int(quantity)
        subtotal += line_total
        item = asdict(product)
        item.update(
            {
                "quantity": int(quantity),
                "line_total": line_total,
            }
        )
        items.append(item)

    return items, subtotal


@app.context_processor
def inject_cart_badge() -> Dict[str, int]:
    """Inject cart item count into all templates for the navigation badge."""
    cart = get_cart()
    count = sum(int(qty) for qty in cart.values())
    return {"cart_item_count": count}


@app.route("/")
def index():
    category = request.args.get("category")

    if category and category.lower() != "all":
        filtered_products = [
            asdict(p) for p in PRODUCTS if p.category.lower() == category.lower()
        ]
    else:
        filtered_products = [asdict(p) for p in PRODUCTS]

    categories = sorted({p.category for p in PRODUCTS})

    return render_template(
        "index.html",
        products=filtered_products,
        categories=categories,
        selected_category=category or "All",
    )


@app.route("/product/<int:product_id>")
def product_detail(product_id: int):
    product = get_product(product_id)
    if not product:
        flash("The product you are looking for does not exist.", "error")
        return redirect(url_for("index"))
    return render_template("product_detail.html", product=asdict(product))


@app.route("/add-to-cart", methods=["POST"])
def add_to_cart():
    product_id = request.form.get("product_id")
    quantity = request.form.get("quantity", "1")

    try:
        product = get_product(int(product_id))
    except (TypeError, ValueError):
        product = None

    if not product:
        flash("Unable to add that product to your cart.", "error")
        return redirect(url_for("index"))

    try:
        qty = max(1, int(quantity))
    except (TypeError, ValueError):
        qty = 1

    cart = get_cart()
    cart_key = str(product.id)
    cart[cart_key] = cart.get(cart_key, 0) + qty
    session["cart"] = cart

    flash(f"Added {qty} � {product.name} to your cart.", "success")

    redirect_target = request.form.get("redirect_to") or url_for("index")
    return redirect(redirect_target)


@app.route("/cart")
def view_cart():
    items, subtotal = cart_items_and_totals()
    shipping = 0 if subtotal == 0 else 7.5
    total = subtotal + shipping
    return render_template(
        "cart.html",
        items=items,
        subtotal=subtotal,
        shipping=shipping,
        total=total,
    )


@app.route("/update-cart", methods=["POST"])
def update_cart():
    cart = get_cart()

    for key, value in request.form.items():
        if not key.startswith("qty_"):
            continue
        product_id = key.replace("qty_", "", 1)
        try:
            qty = int(value)
        except (TypeError, ValueError):
            continue

        if qty <= 0:
            cart.pop(product_id, None)
        else:
            cart[product_id] = qty

    session["cart"] = cart
    flash("Your cart has been updated.", "info")
    return redirect(url_for("view_cart"))


@app.route("/remove-from-cart", methods=["POST"])
def remove_from_cart():
    product_id = request.form.get("product_id")
    cart = get_cart()
    if product_id in cart:
        cart.pop(product_id)
        session["cart"] = cart
        flash("Item removed from your cart.", "info")
    return redirect(url_for("view_cart"))


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    items, subtotal = cart_items_and_totals()
    if not items:
        flash("Your cart is empty. Add some products before checking out.", "error")
        return redirect(url_for("index"))

    shipping = 7.5
    total = subtotal + shipping

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        address = request.form.get("address", "").strip()

        if not (name and email and address):
            flash("Please fill in all required fields.", "error")
            return render_template(
                "checkout.html",
                items=items,
                subtotal=subtotal,
                shipping=shipping,
                total=total,
                name=name,
                email=email,
                address=address,
            )

        # In a real app, you would create an order in the database and process payment here.
        order_summary = {
            "name": name,
            "email": email,
            "address": address,
            "items": items,
            "subtotal": subtotal,
            "shipping": shipping,
            "total": total,
        }

        # Clear the cart after "successful" checkout.
        session["cart"] = {}

        return render_template("checkout.html", order_summary=order_summary)

    return render_template(
        "checkout.html",
        items=items,
        subtotal=subtotal,
        shipping=shipping,
        total=total,
    )


if __name__ == "__main__":
    app.run(debug=True)

