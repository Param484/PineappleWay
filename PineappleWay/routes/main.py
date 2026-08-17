from app import app
from flask import render_template, session, flash, redirect, url_for
from bson import ObjectId
from database.db import users_collection , bookings_collection , packages_collection , contacts_collection
from flask import request
from datetime import datetime

@app.route("/")
def home():

    packages = list(packages_collection.find().limit(3))

    return render_template(
        "home.html",
        packages=packages
    )

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/destination")
def destination():

    search = request.args.get("search", "").strip()

    query = {}

    if search:
        query = {
            "location": {
                "$regex": search,
                "$options": "i"
            }
        }

    destinations = list(packages_collection.find(query))

    return render_template(
        "destination.html",
        destinations=destinations,
        search=search
    )

@app.route("/packages")
def packages():

    search = request.args.get("search", "").strip()

    if search:
        query = {
            "$or": [
                {"name": {"$regex": search, "$options": "i"}},
                {"location": {"$regex": search, "$options": "i"}}
            ]
        }

        packages = list(packages_collection.find(query))

    else:
        packages = list(packages_collection.find())

    return render_template(
        "packages.html",
        packages=packages,
        search=search
    )


@app.route("/package/<package_name>")
def package_details(package_name):

    package = packages_collection.find_one(
        {"name": package_name}
    )

    if not package:
        flash("Package not found.", "warning")
        return redirect(url_for("packages"))

    return render_template(
        "package_details.html",
        package=package
    )



@app.route("/user_dashboard")
def user_dashboard():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    bookings = list(
        bookings_collection.find(
            {"user_id": ObjectId(session["user_id"])}
        )
    )

    total_bookings = len(bookings)

    pending = len([b for b in bookings if b["status"] == "Pending"])
    completed = len([b for b in bookings if b["status"] == "Completed"])

    return render_template(
        "user_dashboard.html",
        bookings=bookings,
        total_bookings=total_bookings,
        pending=pending,
        completed=completed
    )

@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "user_id" not in session:

        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    user = users_collection.find_one(
        {"_id": ObjectId(session["user_id"])}
    )

    if request.method == "POST":

        fullname = request.form["fullname"]
        phone = request.form["phone"]

        users_collection.update_one(

            {"_id": ObjectId(session["user_id"])},

            {
                "$set": {

                    "fullname": fullname,
                    "phone": phone

                }
            }

        )

        session["user_name"] = fullname

        flash("Profile Updated Successfully!", "success")

        return redirect(url_for("profile"))

    return render_template("profile.html", user=user)

@app.route("/contact", methods=["GET","POST"])
def contact():

    if request.method == "POST":

        contacts_collection.insert_one({

            "name": request.form["name"],

            "email": request.form["email"],

            "subject": request.form["subject"],

            "message": request.form["message"],

            "created_at": datetime.utcnow()

        })

        flash("Message sent successfully!", "success")

        return redirect(url_for("contact"))

    return render_template("contact.html")