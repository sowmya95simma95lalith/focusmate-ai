from datetime import datetime, timedelta

WORK_START = "09:00"
WORK_END   = "18:00"
BREAK_AFTER_MIN = 120  # 2h

def _parse_today_time(hhmm: str) -> datetime:
    today = datetime.now().date()
    hh, mm = map(int, hhmm.split(":"))
    return datetime(today.year, today.month, today.day, hh, mm)

def schedule_tasks(tasks):
    """
    Returns list of blocks: [{"title","start","end"}]
    Heuristics:
      1) Tasks with due_time scheduled to finish before due_time (if possible)
      2) Priority order among tasks without due_time (high -> medium -> low)
      3) Insert 5-min break every 2 hours
    """
    if not tasks:
        return []

    start = _parse_today_time(WORK_START)
    end   = _parse_today_time(WORK_END)
    cur = start
    blocks = []
    minutes_since_break = 0

    # Separate tasks with/without deadlines
    with_deadline = []
    without_deadline = []
    for t in tasks:
        due = t.get("due_time")
        if due and isinstance(due, str) and ":" in due:
            try:
                due_dt = _parse_today_time(due)
                with_deadline.append((t, due_dt))
            except Exception:
                without_deadline.append(t)
        else:
            without_deadline.append(t)

    # Sort with deadlines by due_dt (soonest first)
    with_deadline.sort(key=lambda x: x[1])

    # Sort without deadlines by priority then shorter duration
    prio_map = {"high": 0, "medium": 1, "low": 2}
    without_deadline.sort(
        key=lambda t: (prio_map.get(t.get("priority","medium"), 1), int(t.get("duration_min", 60)))
    )

    ordered = [t for (t, _) in with_deadline] + without_deadline

    for t in ordered:
        dur = int(t.get("duration_min", 60))
        # break logic
        if minutes_since_break >= BREAK_AFTER_MIN:
            br_end = cur + timedelta(minutes=5)
            if br_end > end: break
            blocks.append({"title": "🔹 Short Break", "start": cur, "end": br_end})
            cur = br_end
            minutes_since_break = 0

        # if task has due_time, try to ensure we finish before it
        due_str = t.get("due_time")
        if due_str:
            try:
                due_dt = _parse_today_time(due_str)
                latest_start = due_dt - timedelta(minutes=dur)
                if cur > latest_start:
                    # Not enough time before due time; place now anyway (best effort)
                    pass
                # If current time is earlier than a much earlier slot, keep cur
            except Exception:
                pass

        block_end = cur + timedelta(minutes=dur)
        if block_end > end:
            break
        blocks.append({"title": t["title"], "start": cur, "end": block_end})
        cur = block_end
        minutes_since_break += dur

    return blocks
