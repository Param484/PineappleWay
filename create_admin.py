from werkzeug.security import generate_password_hash
from database.db import admins_collection

admin = {
    "fullname": "Administrator",
    "email": "admin@pineappleway.com",
    "password": generate_password_hash("Admin@123")
}

existing = admins_collection.find_one({"email": admin["email"]})

if existing:
    print("Admin already exists.")
else:
    admins_collection.insert_one(admin)
    print("Admin created successfully!")