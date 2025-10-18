import os
import streamlit as st
from openai import OpenAI
from modules.task_manager import add_task, get_tasks, delete_task, clear_tasks
from modules.ai_planner import generate_daily_plan
from modules.scheduler import schedule_tasks
from modules.calendar_export import blocks_to_ics
from modules.task_manager import add_task, get_tasks, delete_task, clear_tasks, toggle_status
import pandas as pd
from modules.exporter import export_plan_pdf, export_plan_md 
import streamlit as st
from modules.task_manager import get_tasks
# from modules.history import current_streak
import pandas as pd
import matplotlib.pyplot as plt
from modules.task_manager import get_tasks, save_tasks
from modules.history import log_day
from modules.history import get_streak_history
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
# --- Page config ---
# st.set_page_config(page_title="FocusMate AI", page_icon="🤖", layout="centered")

st.set_page_config(page_title="FocusMate AI", page_icon="🤖", layout="wide") #added later

# --- Sidebar navigation
page = st.sidebar.radio("📂 Navigation", ["Planner", "Analytics"])

if page == "Planner":
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
        title = col1.text_input("Task title", placeholder="e.g., Finish resume, practice DSA")
        priority = col2.selectbox("Priority", ["high", "medium", "low"], index=1)

        col3, col4, col5 = st.columns([1, 1, 1])
        duration_min = col3.number_input("Duration (min)", min_value=15, max_value=240, value=60, step=15)
        due_time = col4.text_input("Due time (HH:MM)", placeholder="e.g., 14:30")

        category = col5.selectbox("Category", ["JobSearch", "Learning", "Personal", "Work", "Other"], index=0)

        submitted = st.form_submit_button("➕ Add Task")
        if submitted:
            if title.strip():
                due_time_val = due_time.strip() if due_time and ":" in due_time else None
                add_task(
                    title.strip(),
                    priority,
                    duration_min=duration_min,
                    due_time=due_time_val,
                    category=category
                )
                #st.success(f"Added: {title} ({priority}, {duration_min} min, {category}"
                  #      + (f", due {due_time_val}" if due_time_val else "") + ")")
                st.toast(f"✅ Task added: {title}", icon="✅")   # 👈 Toast here
            else:
                st.error("Please enter a task title.")


    # --- Task list ---
    tasks = get_tasks()
    

# --- Check overdue tasks ---
    now = datetime.now().strftime("%H:%M")

    overdue_tasks = [t for t in tasks if t.get("due_time") and t.get("status") == "pending" and t["due_time"] < now]

    if overdue_tasks:
        for t in overdue_tasks:
            st.warning(f"⏰ Task overdue: **{t['title']}** (was due at {t['due_time']})")




    st.subheader("📋 Your Tasks")
    if not tasks:
        st.info("No tasks yet — add a few above.")
    else:
        # Render tasks with delete buttons
        for i, t in enumerate(tasks):
            cols = st.columns([7, 2])
            task_text = f"**{i+1}. {t['title']}** — _{t.get('priority','medium')}_ ({t['duration_min']} min) | 🏷 {t.get('category','General')}"
            if t.get("status", "pending") == "done":
                task_text = f"~~{task_text}~~"   # strikethrough when done
            # Checkbox to toggle status
            checked = cols[0].checkbox(
                task_text,
                value=(t.get("status", "pending") == "done"),
                key=f"chk_{i}"
            )


            # If user ticks/unticks, update status
            # if checked and t.get("status", "pending") != "done":
            #     tasks[i]["status"] = "done"
            #     save_tasks(tasks)
            #     st.rerun()
            # elif not checked and t.get("status", "pending") == "done":
            #     tasks[i]["status"] = "pending"
            #     save_tasks(tasks)
            #     st.rerun()
            #########################################################
            # if checked and t.get("status", "pending") != "done":
            #     tasks[i]["status"] = "done"
            #     save_tasks(tasks)
            #     st.toast(f"✅ Task completed: {t['title']}", icon="🎉")   # 👈 Toast here
            #     st.rerun()
            # elif not checked and t.get("status", "pending") == "done":
            #     tasks[i]["status"] = "pending"
            #     save_tasks(tasks)
            #     st.toast(f"↩️ Task reset to pending: {t['title']}", icon="↩️")   # 👈 Toast here
            #     st.rerun()
            ########################################################
            if checked and t.get("status", "pending") != "done":
                tasks[i]["status"] = "done"
                tasks[i]["completed_at"] = datetime.now().strftime("%H:%M")
                save_tasks(tasks)
                st.toast(f"✅ Task completed: {t['title']}", icon="🎉")
                st.rerun()
            elif not checked and t.get("status", "pending") == "done":
                tasks[i]["status"] = "pending"
                tasks[i].pop("completed_at", None)  # remove timestamp
                save_tasks(tasks)
                st.toast(f"↩️ Task reset to pending: {t['title']}", icon="↩️")
                st.rerun()


            # # Delete button
            # if cols[1].button("❌ Delete", key=f"del_{i}"):
            #     delete_task(i)
            #     st.rerun()
            if cols[1].button("❌ Delete", key=f"del_{i}"):
                delete_task(i)
                st.toast(f"🗑️ Task deleted: {t['title']}", icon="🗑️")   # 👈 Toast here
                st.rerun()

        colA, colB = st.columns(2)
        
        
        # if colA.button("🧹 Clear All"):
        #     clear_tasks()
        #     st.rerun()
        if colA.button("🧹 Clear All"):
            clear_tasks()
            st.toast("🧹 All tasks cleared!", icon="🧹")   # 👈 Toast here
            st.rerun()


        if colB.button("⚡ Generate Customized Daily Plan"):
            plan = generate_daily_plan()
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
                        data=f,
                        file_name="ai_plan.pdf",
                        mime="application/pdf"
                    )

            # Markdown export
                with open("ai_plan.md", "w", encoding="utf-8") as f:
                    f.write(plan)
                with open("ai_plan.md", "rb") as f:
                    st.download_button(
                    "⬇️ Download as Markdown",
                    data=f,
                    file_name="ai_plan.md",
                    mime="text/markdown"
                    )
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
if page == "Analytics":
    st.title("📊 Analytics Dashboard")

    tasks = get_tasks()

    if not tasks:
        st.info("No tasks yet — add some in the Planner page.")
    else:
        import pandas as pd
        import matplotlib.pyplot as plt

        df = pd.DataFrame(tasks)

        # --- Priority Breakdown
        st.subheader("🔺 Task Priority Breakdown")
        prio_counts = df['priority'].value_counts()
        fig, ax = plt.subplots()
        ax.pie(prio_counts, labels=prio_counts.index, autopct='%1.1f%%', startangle=90)
        ax.axis("equal")
        st.pyplot(fig)

        # --- Time Allocation by Priority
        st.subheader("⏱️ Time Allocation (minutes) by Priority")
        time_alloc = df.groupby("priority")["duration_min"].sum()
        fig, ax = plt.subplots()
        time_alloc.plot(kind="bar", ax=ax, color=["red","orange","green"])
        ax.set_ylabel("Total Minutes")
        st.pyplot(fig)

        # --- Completion Rate
        st.subheader("✅ Completion Rate")
        status_counts = df['status'].value_counts()
        completed = status_counts.get("done", 0)
        pending = status_counts.get("pending", 0)
        st.metric("Completed Tasks", completed)
        st.metric("Pending Tasks", pending)

        # --- Streak Tracker
        # # from modules.history import current_streak
        # st.subheader("🔥 Daily Streak")
        # streak = current_streak()
        # st.write(f"You are on a **{streak}-day streak** of generating plans!")

        # --- Streak History Chart ---
        st.subheader("📈 Streak History Over Time")
        dates = get_streak_history()
        if dates:
            df_hist = pd.DataFrame({"Date": pd.to_datetime(dates)})
            df_hist["Value"] = 1
            df_hist = df_hist.groupby("Date").sum().cumsum().reset_index()

            fig, ax = plt.subplots()
            ax.plot(df_hist["Date"], df_hist["Value"], marker="o")
            ax.set_xlabel("Date")
            ax.set_ylabel("Cumulative Days Planned")
            ax.set_title("Streak Progress")
            st.pyplot(fig)
        else:
            st.info("No streak history yet. Generate a plan to start tracking.")
        st.subheader("🏷 Task Categories")
        if "category" in df.columns:
            cat_counts = df["category"].value_counts()
            fig, ax = plt.subplots()
            cat_counts.plot(kind="bar", ax=ax)
            ax.set_ylabel("Number of Tasks")
            st.pyplot(fig)

            # Time allocation by category
            st.subheader("⏱ Time Allocation by Category")
            cat_time = df.groupby("category")["duration_min"].sum()
            fig, ax = plt.subplots()
            cat_time.plot(kind="bar", ax=ax, color="skyblue")
            ax.set_ylabel("Total Minutes")
            st.pyplot(fig)
        # --- Productivity Metric ---
        st.subheader("📈 Productivity")

        on_time_done = 0
        with_due_time = 0

        for t in tasks:
            if t.get("due_time"):
                with_due_time += 1
                if t.get("status") == "done" and t.get("completed_at"):
                    if t["completed_at"] <= t["due_time"]:
                        on_time_done += 1

        if with_due_time > 0:
            productivity = round((on_time_done / with_due_time) * 100, 1)
            st.metric("On-Time Productivity", f"{productivity}%")
        else:
            st.info("No tasks with due times yet.")

