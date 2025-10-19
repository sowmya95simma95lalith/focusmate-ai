import os
from pymongo import MongoClient
from dotenv import load_dotenv
import streamlit as st
# Load environment variables from .env
load_dotenv()

# Get Mongo URI from .env
MONGO_URI = os.getenv("MONGO_URI")
import certifi

if not MONGO_URI:
    raise ValueError("❌ MONGO_URI not found. Please set it in your .env file.")

# Connect to MongoDB
# client = MongoClient(MONGO_URI)
client = MongoClient(MONGO_URI, tls=True, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)

# Database and Collection
db = client["focusmate_ai"]   # database name
tasks_collection = db["tasks"]

# --- CRUD Functions ---

def add_task(user, task):
    """Insert a new task for a specific user."""
    task["user"] = user
    tasks_collection.insert_one(task)

def get_tasks(user):
    """Retrieve all tasks for a user."""
    return list(tasks_collection.find({"user": user}, {"_id": 0}))

def update_task(user, title, update_fields):
    """Update fields of a task by title for a user."""
    tasks_collection.update_one(
        {"user": user, "title": title},
        {"$set": update_fields}
    )

def delete_task(user, title):
    """Delete a task by title for a user."""
    tasks_collection.delete_one({"user": user, "title": title})

def clear_tasks(user):
    """Delete all tasks for a user."""
    tasks_collection.delete_many({"user": user})
try:
    st.sidebar.markdown("### 🔍 DB Debug Info")
    st.sidebar.write("MONGO_URI loaded?", bool(os.getenv("MONGO_URI")))
    st.sidebar.write("Connected DB:", db.name)
    st.sidebar.write("Collections:", db.list_collection_names())
except Exception as e:
    st.sidebar.error(f"DB Debug Error: {e}")
