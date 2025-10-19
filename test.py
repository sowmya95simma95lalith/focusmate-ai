import os
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
# import certifi
# client = MongoClient(MONGO_URI, tls=True, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)

print("MONGO_URI loaded?", bool(MONGO_URI))

try:
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
    db = client["focusmate_ai"]
    print("Databases:", client.list_database_names())
    print("Collections in focusmate_ai:", db.list_collection_names())
except Exception as e:
    print("❌ Connection failed:", e)
