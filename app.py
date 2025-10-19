import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from modules.db import add_task, get_tasks, update_task, delete_task, clear_tasks
from modules.ai_planner import generate_daily_plan
from modules.calendar_export import blocks_to_ics
from modules.scheduler import schedule_tasks
from modules.exporter import export_plan_pdf
from modules.history import log_day, current_streak, get_streak_history

# --- Page Config ---
st.set_page_config(page_title="FocusMate AI", page_icon="🤖", layout="wide")

# --- Sidebar ---
st.sidebar.header("🔑 User")
username = st.sidebar.text_input("Enter your username", value="guest")

page = st.sidebar.radio("📂 Navigation", ["Planner", "Analytics"])

# ============================
# PLANNER PAGE
# ============================
if page == "Planner":
    st.markdown("# 🤖 FocusMate AI — Daily Productivity Assistant")
    st.caption("Add tasks, set priorities, and generate a smart daily plan powered by AI.")

    # --- Task Input Form ---
    with st.form("add_task_form", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        title = col1.text_input("Task title")
        priority = col2.selectbox("Priority", ["high", "medium", "low"], index=1)

        col3, col4, col5 = st.columns([1, 1, 1])
        duration_min = col3.number_input("Duration (min)", min_value=15, max_value=240, value=60, step=15)
        due_time = col4.text_input("Due time (HH:MM)", placeholder="e.g., 14:30")
        category = col5.selectbox("Category", ["JobSearch", "Learning", "Personal", "Work", "Other"], index=0)

        submitted = st.form_submit_button("➕ Add Task")
        if submitted and title.strip():
            due_time_val = due_time.strip() if due_time and ":" in due_time else None
            add_task(username, {
                "title": title.strip(),
                "priority": priority,
                "duration_min": duration_min,
                "due_time": due_time_val,
                "status": "pending",
                "category": category
            })
            st.toast(f"✅ Task added: {title}", icon="✅")
            st.rerun()

    # --- Task List ---
    tasks = get_tasks(username)
    st.subheader("📋 Your Tasks")

    if not tasks:
        st.info("No tasks yet — add a few above.")
    else:
        for i, t in enumerate(tasks):
            cols = st.columns([7, 2])

            task_text = f"**{i+1}. {t['title']}** — _{t.get('priority','medium')}_ ({t['duration_min']} min) | 🏷 {t.get('category','General')}"
            if t.get("status") == "done":
                task_text = f"~~{task_text}~~"

            checked = cols[0].checkbox(
                task_text,
                value=(t.get("status") == "done"),
                key=f"chk_{i}"
            )

            if checked and t.get("status") != "done":
                update_task(username, t["title"], {
                    "status": "done",
                    "completed_at": datetime.now().strftime("%H:%M")
                })
                st.toast(f"✅ Task completed: {t['title']}", icon="🎉")
                st.rerun()

            elif not checked and t.get("status") == "done":
                update_task(username, t["title"], {"status": "pending"})
                st.toast(f"↩️ Task reset: {t['title']}", icon="↩️")
                st.rerun()

            if cols[1].button("❌ Delete", key=f"del_{i}"):
                delete_task(username, t["title"])
                st.toast(f"🗑️ Task deleted: {t['title']}", icon="🗑️")
                st.rerun()

        colA, colB = st.columns(2)

        if colA.button("🧹 Clear All"):
            clear_tasks(username)
            st.toast("🧹 All tasks cleared!", icon="🧹")
            st.rerun()

        if colB.button("⚡ Generate Customized Daily Plan"):
            plan = generate_daily_plan(username)
            log_day()
            st.markdown("---")
            st.subheader("🗓️ Your Customized Plan")
            st.write(plan)
            if plan:
                with open("ai_plan.pdf", "wb") as f:
                    export_plan_pdf(plan, "ai_plan.pdf")
                with open("ai_plan.pdf", "rb") as f:
                    st.download_button(
                        "⬇️ Download as PDF",
                        data=f.read(),
                        file_name="ai_plan.pdf",
                        mime="application/pdf"
                    )

    # --- Schedule ---
    st.subheader("⏱️ Time-Boxed Schedule")
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
            st.dataframe(df, width="stretch")
            ics_bytes = blocks_to_ics(blocks)
            st.download_button(
                "📅 Export to Calendar (.ics)",
                data=ics_bytes,
                file_name="focusmate_plan.ics",
                mime="text/calendar"
            )

# ============================
# ANALYTICS PAGE
# ============================
if page == "Analytics":
    st.title("📊 Analytics Dashboard")
    tasks = get_tasks(username)

    if not tasks:
        st.info("No tasks yet — add some in the Planner page.")
    else:
        df = pd.DataFrame(tasks)

        st.subheader("🔺 Priority Breakdown")
        prio_counts = df["priority"].value_counts()
        fig, ax = plt.subplots()
        ax.pie(prio_counts, labels=prio_counts.index, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)

        st.subheader("⏱ Time Allocation by Priority")
        time_alloc = df.groupby("priority")["duration_min"].sum()
        fig, ax = plt.subplots()
        time_alloc.plot(kind="bar", ax=ax, color=["red","orange","green"])
        ax.set_ylabel("Minutes")
        st.pyplot(fig)

        st.subheader("✅ Completion Rate")
        status_counts = df["status"].value_counts()
        completed = status_counts.get("done", 0)
        pending = status_counts.get("pending", 0)
        st.metric("Completed Tasks", completed)
        st.metric("Pending Tasks", pending)

        st.subheader("🔥 Daily Streak")
        streak = current_streak()
        st.write(f"You are on a **{streak}-day streak**")

        st.subheader("📈 Streak History")
        dates = get_streak_history()
        if dates:
            df_hist = pd.DataFrame({"Date": pd.to_datetime(dates)})
            df_hist["Value"] = 1
            df_hist = df_hist.groupby("Date").sum().cumsum().reset_index()
            fig, ax = plt.subplots()
            ax.plot(df_hist["Date"], df_hist["Value"], marker="o")
            st.pyplot(fig)
        # --- Productivity Metric ---
        st.subheader("📈 Productivity")

        with_due = [t for t in tasks if t.get("due_time")]
        on_time = [
            t for t in with_due
            if t.get("status") == "done"
            and t.get("completed_at")
            and t["completed_at"] <= t["due_time"]
        ]

        if with_due:
            pct = round((len(on_time) / len(with_due)) * 100, 1)
            st.metric("On-Time Productivity", f"{pct}%")
        else:
            st.info("No tasks with due times yet.")
