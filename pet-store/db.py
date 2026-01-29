import os
from pymongo import MongoClient

MONGO_URI = os.environ.get("DB_URI", "mongodb://mongo-store:27017")
STORE_ID = os.environ.get("STORE_ID", "1")

client = MongoClient(MONGO_URI)
db = client.get_database("petstore_db")

pettypes = db[f"pettypes_store_{STORE_ID}"]
pets = db[f"pets_store_{STORE_ID}"]