import json, os
from datetime import date

HISTORY_FILE = "data/history.json"

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f)

def log_day():
    """Log today's date when a plan is generated."""
    history = load_history()
    today_str = str(date.today())
    if today_str not in history:
        history.append(today_str)
        save_history(history)

def get_streak_history():
    """Return all logged days as a list of strings."""
    return load_history()

def current_streak():
    """Return current streak count (consecutive days)."""
    history = sorted(get_streak_history())
    if not history:
        return 0
    streak = 1
    from datetime import datetime, timedelta
    today = date.today()
    # walk backwards from today
    for i in range(1, len(history)):
        d1 = datetime.strptime(history[-i], "%Y-%m-%d").date()
        d2 = datetime.strptime(history[-i-1], "%Y-%m-%d").date()
        if (d1 - d2).days == 1:
            streak += 1
        else:
            break
    # check if today is included
    if str(today) != history[-1]:
        return 0
    return streak
