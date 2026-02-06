from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///fleet.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "change-me-in-production"

db = SQLAlchemy(app)


class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate_number = db.Column(db.String(64), unique=True, nullable=False)
    make = db.Column(db.String(64), nullable=False)
    model = db.Column(db.String(64), nullable=False)
    year = db.Column(db.Integer, nullable=True)
    driver_name = db.Column(db.String(128), nullable=True)
    status = db.Column(db.String(32), nullable=False, default="Active")
    mileage = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<Vehicle {self.plate_number}>"


@app.route("/", methods=["GET"])
def index():
    status_filter = request.args.get("status", "all")
    search_query = request.args.get("q", "").strip()

    query = Vehicle.query

    if status_filter and status_filter.lower() != "all":
        query = query.filter_by(status=status_filter)

    if search_query:
        like_pattern = f"%{search_query}%"
        query = query.filter(
            db.or_(
                Vehicle.plate_number.ilike(like_pattern),
                Vehicle.make.ilike(like_pattern),
                Vehicle.model.ilike(like_pattern),
                Vehicle.driver_name.ilike(like_pattern),
            )
        )

    vehicles = query.order_by(Vehicle.created_at.desc()).all()

    total = Vehicle.query.count()
    active = Vehicle.query.filter_by(status="Active").count()
    maintenance = Vehicle.query.filter_by(status="In Maintenance").count()
    retired = Vehicle.query.filter_by(status="Retired").count()

    return render_template(
        "index.html",
        vehicles=vehicles,
        status_filter=status_filter,
        search_query=search_query,
        stats={"total": total, "active": active, "maintenance": maintenance, "retired": retired},
    )


@app.route("/vehicle/new", methods=["GET", "POST"])
def create_vehicle():
    if request.method == "POST":
        plate_number = request.form.get("plate_number", "").strip()
        make = request.form.get("make", "").strip()
        model = request.form.get("model", "").strip()
        year = request.form.get("year", "").strip()
        driver_name = request.form.get("driver_name", "").strip()
        status = request.form.get("status", "Active").strip()
        mileage = request.form.get("mileage", "").strip()
        notes = request.form.get("notes", "").strip()

        if not plate_number or not make or not model:
            flash("Plate number, make, and model are required.", "error")
            return redirect(url_for("create_vehicle"))

        existing = Vehicle.query.filter_by(plate_number=plate_number).first()
        if existing:
            flash("A vehicle with this plate number already exists.", "error")
            return redirect(url_for("create_vehicle"))

        try:
            year_val = int(year) if year else None
        except ValueError:
            year_val = None

        try:
            mileage_val = int(mileage) if mileage else None
        except ValueError:
            mileage_val = None

        vehicle = Vehicle(
            plate_number=plate_number,
            make=make,
            model=model,
            year=year_val,
            driver_name=driver_name or None,
            status=status or "Active",
            mileage=mileage_val,
            notes=notes or None,
        )

        db.session.add(vehicle)
        db.session.commit()
        flash("Vehicle added successfully.", "success")
        return redirect(url_for("index"))

    return render_template("vehicle_form.html", vehicle=None)


@app.route("/vehicle/<int:vehicle_id>", methods=["GET"])
def vehicle_detail(vehicle_id: int):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    return render_template("vehicle_detail.html", vehicle=vehicle)


@app.route("/vehicle/<int:vehicle_id>/edit", methods=["GET", "POST"])
def edit_vehicle(vehicle_id: int):
    vehicle = Vehicle.query.get_or_404(vehicle_id)

    if request.method == "POST":
        plate_number = request.form.get("plate_number", "").strip()
        make = request.form.get("make", "").strip()
        model = request.form.get("model", "").strip()
        year = request.form.get("year", "").strip()
        driver_name = request.form.get("driver_name", "").strip()
        status = request.form.get("status", "Active").strip()
        mileage = request.form.get("mileage", "").strip()
        notes = request.form.get("notes", "").strip()

        if not plate_number or not make or not model:
            flash("Plate number, make, and model are required.", "error")
            return redirect(url_for("edit_vehicle", vehicle_id=vehicle.id))

        existing = Vehicle.query.filter_by(plate_number=plate_number).first()
        if existing and existing.id != vehicle.id:
            flash("Another vehicle with this plate number already exists.", "error")
            return redirect(url_for("edit_vehicle", vehicle_id=vehicle.id))

        try:
            year_val = int(year) if year else None
        except ValueError:
            year_val = None

        try:
            mileage_val = int(mileage) if mileage else None
        except ValueError:
            mileage_val = None

        vehicle.plate_number = plate_number
        vehicle.make = make
        vehicle.model = model
        vehicle.year = year_val
        vehicle.driver_name = driver_name or None
        vehicle.status = status or "Active"
        vehicle.mileage = mileage_val
        vehicle.notes = notes or None

        db.session.commit()
        flash("Vehicle updated successfully.", "success")
        return redirect(url_for("vehicle_detail", vehicle_id=vehicle.id))

    return render_template("vehicle_form.html", vehicle=vehicle)


@app.route("/vehicle/<int:vehicle_id>/retire", methods=["POST"])
def retire_vehicle(vehicle_id: int):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    vehicle.status = "Retired"
    db.session.commit()
    flash("Vehicle marked as retired.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

