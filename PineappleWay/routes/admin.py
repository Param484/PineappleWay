from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from database.db import (
    users_collection,
    packages_collection,
    bookings_collection,
    admins_collection,
    contacts_collection
)
from app import app

from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from app import app
from database.db import admins_collection
from bson import ObjectId
from database.db import packages_collection
import os
from werkzeug.utils import secure_filename

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        admin = admins_collection.find_one({"email": email})

        if admin and check_password_hash(admin["password"], password):

            session["admin_id"] = str(admin["_id"])
            session["admin_name"] = admin["fullname"]

            flash("Welcome Admin!", "success")

            return redirect(url_for("admin_dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    total_users = users_collection.count_documents({})
    total_packages = packages_collection.count_documents({})
    total_bookings = bookings_collection.count_documents({})
    pending_bookings = bookings_collection.count_documents(
        {"status": "Pending"}
    )

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_packages=total_packages,
        total_bookings=total_bookings,
        pending_bookings=pending_bookings
    )

@app.route("/admin/packages")
def admin_packages():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    search = request.args.get("search", "")

    if search:
        packages = list(
            packages_collection.find({
                "$or": [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"location": {"$regex": search, "$options": "i"}}
                ]
            })
        )
    else:
        packages = list(packages_collection.find())

    return render_template(
        "admin_packages.html",
        packages=packages,
        search=search
    )


@app.route("/admin/packages/add", methods=["GET", "POST"])
def add_package():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    if request.method == "POST":

        image = request.files["image"]

        filename = ""

        if image and image.filename != "":
            filename = secure_filename(image.filename)

            image.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

        package = {

            "name": request.form["name"],
            "location": request.form["location"],
            "duration": request.form["duration"],
            "price": int(request.form["price"]),
            "hotel": request.form["hotel"],
            "meals": request.form["meals"],
            "guide": request.form["guide"],
            "image": filename,
            "description": request.form["description"],

            "itinerary": request.form["itinerary"].splitlines(),

            "included": request.form["included"].splitlines(),

            "excluded": request.form["excluded"].splitlines(),

        }

        packages_collection.insert_one(package)

        flash("Package added successfully!", "success")

        return redirect(url_for("admin_packages"))

    return render_template("add_package.html")

@app.route("/admin/packages/edit/<package_id>", methods=["GET", "POST"])
def edit_package(package_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    package = packages_collection.find_one(
        {"_id": ObjectId(package_id)}
    )

    if not package:
        flash("Package not found.", "danger")
        return redirect(url_for("admin_packages"))

    if request.method == "POST":

        image = request.files["image"]

        filename = package["image"]

        if image and image.filename != "":
            filename = secure_filename(image.filename)

            image.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

        packages_collection.update_one(

            {"_id": ObjectId(package_id)},

            {
                "$set": {

                    "name": request.form["name"],
                    "location": request.form["location"],
                    "duration": request.form["duration"],
                    "price": int(request.form["price"]),
                    "hotel": request.form["hotel"],
                    "meals": request.form["meals"],
                    "guide": request.form["guide"],
                    "image": filename,
                    "description": request.form["description"],
                    "itinerary": request.form["itinerary"].splitlines(),

                    "included": request.form["included"].splitlines(),

                    "excluded": request.form["excluded"].splitlines(),

                }

            }

        )

        flash("Package updated successfully!", "success")

        return redirect(url_for("admin_packages"))

    return render_template(
        "edit_package.html",
        package=package
    )

@app.route("/admin/packages/delete/<package_id>")
def delete_package(package_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    packages_collection.delete_one(
        {"_id": ObjectId(package_id)}
    )

    flash("Package Deleted!", "success")

    return redirect(url_for("admin_packages"))

@app.route("/admin/bookings")
def admin_bookings():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    search = request.args.get("search", "")
    status = request.args.get("status", "")

    query = {}

    if search:
        query["$or"] = [
            {"user_name": {"$regex": search, "$options": "i"}},
            {"package_name": {"$regex": search, "$options": "i"}}
        ]

    if status:
        query["status"] = status

    bookings = list(bookings_collection.find(query))

    return render_template(
        "admin_bookings.html",
        bookings=bookings,
        search=search,
        status=status
    )

@app.route("/admin/bookings/update/<booking_id>", methods=["GET", "POST"])
def update_booking(booking_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    booking = bookings_collection.find_one(
        {"_id": ObjectId(booking_id)}
    )

    if not booking:
        flash("Booking not found.", "danger")
        return redirect(url_for("admin_bookings"))

    if request.method == "POST":

        new_status = request.form["status"]

        bookings_collection.update_one(
            {"_id": ObjectId(booking_id)},
            {
                "$set": {
                    "status": new_status
                }
            }
        )

        flash(
            f"Booking status changed to {new_status}.",
            "success"
        )

        return redirect(url_for("admin_bookings"))

    return render_template(
        "update_booking.html",
        booking=booking
    )

@app.route("/admin/users")
def admin_users():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    search = request.args.get("search", "")

    if search:

        users = list(
            users_collection.find({
                "$or":[
                    {"fullname":{"$regex":search,"$options":"i"}},
                    {"email":{"$regex":search,"$options":"i"}}
                ]
            })
        )

    else:

        users = list(users_collection.find())

    for user in users:

        user["total_bookings"] = bookings_collection.count_documents(
            {"user_id": user["_id"]}
        )

    return render_template(
        "admin_users.html",
        users=users,
        search=search
    )

    return render_template(
        "admin_users.html",
        users=users
    )

@app.route("/admin/users/delete/<user_id>")
def delete_user(user_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    users_collection.delete_one(
        {"_id": ObjectId(user_id)}
    )

    bookings_collection.delete_many(
    {"user_id": ObjectId(user_id)}
)

    flash("User deleted successfully!", "success")

    return redirect(url_for("admin_users"))

@app.route("/admin/logout")
def admin_logout():

    session.pop("admin_id", None)
    session.pop("admin_name", None)

    flash("Logged out successfully.", "success")

    return redirect(url_for("admin_login"))

@app.route("/admin/contacts")
def admin_contacts():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    contacts = list(
        contacts_collection.find().sort("created_at",-1)
    )

    return render_template(
        "admin_contacts.html",
        contacts=contacts
    )

@app.route("/admin/contact/<id>")
def view_contact(id):

    contact = contacts_collection.find_one(
        {"_id":ObjectId(id)}
    )

    return render_template(
        "view_contact.html",
        contact=contact
    )

@app.route("/admin/contact/delete/<id>")
def delete_contact(id):

    contacts_collection.delete_one(
        {"_id":ObjectId(id)}
    )

    flash("Message deleted.","success")

    return redirect(url_for("admin_contacts"))