from flask import render_template, request, redirect, url_for, flash , session
from app import app
from database.db import users_collection
from werkzeug.security import generate_password_hash

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        fullname = request.form["fullname"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Check password match
        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("register"))

        # Check if email already exists
        existing_user = users_collection.find_one({"email": email})

        if existing_user:
            flash("Email already registered!", "warning")
            return redirect(url_for("register"))

        # Create user document
        user = {
            "fullname": fullname,
            "email": email,
            "phone": phone,
            "password": generate_password_hash(password)
        }

        users_collection.insert_one(user)

        flash("Registration Successful! Please Login.", "success")

        return redirect(url_for("login"))

    return render_template("register.html")

from werkzeug.security import check_password_hash

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = users_collection.find_one({"email": email})

        if user:

            if check_password_hash(user["password"], password):

                session["user_id"] = str(user["_id"])
                session["user_name"] = user["fullname"]
                session["user_email"] = user["email"]

                print(session)

                flash("Login Successful!", "success")

                return redirect(url_for("user_dashboard"))

            else:

                flash("Incorrect Password!", "danger")

        else:

            flash("User does not exist!", "warning")

    return render_template("login.html")

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully.", "success")

    return redirect(url_for("login"))