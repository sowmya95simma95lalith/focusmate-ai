from datetime import datetime
from textwrap import dedent

def _fmt(dt: datetime) -> str:
    # ICS uses UTC or local in "floating time". We'll use local floating for simplicity.
    return dt.strftime("%Y%m%dT%H%M%S")

def blocks_to_ics(blocks, calendar_name="FocusMate AI Plan"):
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:-//{calendar_name}//EN",
    ]
    for b in blocks:
        if "Short Break" in b["title"]:
            # optional: skip breaks from calendar
            continue
        start = _fmt(b["start"])
        end   = _fmt(b["end"])
        uid = f"{start}-{end}-{abs(hash(b['title']))}@focusmate"
        event = f"""
        BEGIN:VEVENT
        UID:{uid}
        DTSTAMP:{start}
        DTSTART:{start}
        DTEND:{end}
        SUMMARY:{b['title']}
        END:VEVENT
        """
        lines.append(dedent(event).strip())
    lines.append("END:VCALENDAR")
    return "\n".join(lines).encode("utf-8")
