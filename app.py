import os
import streamlit as st
from openai import OpenAI
from modules.task_manager import add_task, get_tasks, delete_task, clear_tasks
from modules.ai_planner import generate_daily_plan
from modules.scheduler import schedule_tasks
from modules.calendar_export import blocks_to_ics
from modules.task_manager import add_task, get_tasks, delete_task, clear_tasks, toggle_status
import pandas as pd

# --- Page config ---
st.set_page_config(page_title="FocusMate AI", page_icon="🤖", layout="centered")

st.markdown("# 🤖 FocusMate AI — Daily Productivity Assistant")
st.caption("Add tasks, set priorities, and generate a smart daily plan powered by AI.")

# --- Sidebar: API key status ---
api_key_present = bool(os.getenv("OPENAI_API_KEY"))
with st.sidebar:
    st.markdown("### API Key")
    if api_key_present:
        st.success("OPENAI_API_KEY detected ✅")
    else:
        st.warning("OPENAI_API_KEY not found. Fallback plan will be used.")

# --- Task input form ---
with st.form("add_task_form", clear_on_submit=True):
    col1, col2 = st.columns([3, 1])
    title = col1.text_input("Task title", placeholder="e.g., Finish resume, practice DSA, apply to 3 jobs")
    priority = col2.selectbox("Priority", ["high", "medium", "low"], index=1)
    col3, col4, col5 = st.columns([1,1,1])
    duration_min = col3.number_input("Duration (min)", min_value=15, max_value=240, value=60, step=15)
    due_time = col4.text_input("Due time (HH:MM)", placeholder="e.g., 14:30")
    submitted = st.form_submit_button("➕ Add Task")
    if submitted:
        if title.strip():
            due_time_val = due_time.strip() if due_time and ":" in due_time else None
            add_task(title.strip(), priority, duration_min=duration_min, due_time=due_time_val)
            st.success(f"Added: {title} ({priority}, {duration_min} min"
                       + (f", due {due_time_val}" if due_time_val else "") + ")")
        else:
            st.error("Please enter a task title.")


# --- Task list ---
tasks = get_tasks()
st.subheader("📋 Your Tasks")
if not tasks:
    st.info("No tasks yet — add a few above.")
else:
    # Render tasks with delete buttons
    for i, t in enumerate(tasks):
        cols = st.columns([6, 2])
        cols[0].write(f"**{i+1}. {t['title']}** — _{t.get('priority','medium')}_")
        if cols[1].button("Delete", key=f"del_{i}"):
            delete_task(i)
            st.rerun()

    colA, colB = st.columns(2)
    if colA.button("🧹 Clear All"):
        clear_tasks()
        st.rerun()
    if colB.button("⚡ Generate Customized Daily Plan"):
        plan = generate_daily_plan()
        st.markdown("---")
        st.subheader("🗓️ Your Customized Plan")
        st.write(plan)
st.subheader("⏱️ Time-Boxed Schedule (Deadline-Aware)")
if tasks:
    blocks = schedule_tasks(tasks)
    if not blocks:
        st.info("Not enough time in the work window to schedule tasks.")
    else:
        df = pd.DataFrame([{
            "Start": b["start"].strftime("%H:%M"),
            "End": b["end"].strftime("%H:%M"),
            "Task": b["title"]
        } for b in blocks])
        st.dataframe(df, use_container_width=True)

        ics_bytes = blocks_to_ics(blocks)
        st.download_button(
            "📅 Export to Calendar (.ics)",
            data=ics_bytes,
            file_name="focusmate_plan.ics",
            mime="text/calendar"
        )
else:
    st.info("Add tasks to see a schedule.")
