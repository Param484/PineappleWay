import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["PineappleWay"]

users_collection = db["users"]

packages_collection = db["packages"]

bookings_collection = db["bookings"]

admins_collection = db["admins"]

contacts_collection = db["contacts"]