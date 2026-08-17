from flask import render_template, request, redirect, url_for, flash, session
from app import app
from database.db import bookings_collection , users_collection , packages_collection
from bson import ObjectId
from datetime import datetime
import random

@app.route("/booking", methods=["GET", "POST"])
def booking():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    # Get selected package from URL
    package_name = request.args.get("package")
    package = packages_collection.find_one(
    {"name": package_name}
)

    # Get logged-in user from MongoDB
    user = users_collection.find_one(
        {"_id": ObjectId(session["user_id"])}
    )

    if request.method == "POST":

        booking_id = "PW" + str(random.randint(100000, 999999))

        booking = {

            "booking_id": booking_id,

            "user_id": ObjectId(session["user_id"]),

            "user_name": user["fullname"],

            "user_email": user["email"],

            "phone": user["phone"],

            "package_name": request.form["package_name"],

            "travel_date": request.form["travel_date"],

            "travellers": int(request.form["travellers"]),

            "special_request": request.form["special_request"],

            "status": "Pending",

            "created_at": datetime.utcnow()

        }

        bookings_collection.insert_one(booking)

        flash("Booking Successful!", "success")

        return redirect(url_for("my_bookings"))

    return render_template(
        "booking.html",
        user=user,
        package=package
    )

@app.route("/my_bookings")
def my_bookings():

    if "user_id" not in session:
        return redirect(url_for("login"))

    bookings = list(
        bookings_collection.find(
            {"user_id": ObjectId(session["user_id"])}
        )
    )

    return render_template(
        "my_bookings.html",
        bookings=bookings
    )