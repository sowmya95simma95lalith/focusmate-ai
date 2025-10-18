import json
import os
from datetime import datetime
from json import JSONDecodeError

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "tasks.json")

def _ensure_store():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

def load_tasks():
    _ensure_store()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # ensure it's a list
            return data if isinstance(data, list) else []
    except (JSONDecodeError, OSError):
        # file is empty or corrupted → reset to empty list
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return []

def save_tasks(tasks):
    _ensure_store()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4)

def add_task(title, priority="medium", due_date=None, duration_min=60, due_time=None):
    tasks = load_tasks()
    task = {
        "title": title,
        "priority": priority,
        "due_date": due_date,                 # keep for future
        "due_time": due_time,                 # "HH:MM" or None
        "duration_min": int(duration_min) if str(duration_min).isdigit() else 60,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "pending",
    }
    tasks.append(task)
    save_tasks(tasks)

def view_tasks():
    tasks = load_tasks()
    for i, t in enumerate(tasks, 1):
        print(f"{i}. {t['title']} ({t['priority']}) - {t['status']}")

def get_tasks():
    return load_tasks()

def clear_tasks():
    save_tasks([])

def delete_task(index_zero_based: int):
    tasks = load_tasks()
    if 0 <= index_zero_based < len(tasks):
        tasks.pop(index_zero_based)
        save_tasks(tasks)
def toggle_status(index_zero_based: int):
    tasks = load_tasks()
    if 0 <= index_zero_based < len(tasks):
        tasks[index_zero_based]["status"] = (
            "done" if tasks[index_zero_based].get("status") != "done" else "pending"
        )
        save_tasks(tasks)
 
