import os
from openai import OpenAI

print("API Key Found?", bool(os.getenv("OPENAI_API_KEY")))

client = OpenAI()
resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Say hi in 3 words."}],
)
print(resp.choices[0].message.content)




#app working
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
        # Render tasks with status + done/reset/delete buttons
        for i, t in enumerate(tasks):
            cols = st.columns([6, 2, 2, 2])

            # Task title with status icon
            status_icon = "✅" if t.get("status", "pending") == "done" else "⏳"
            cols[0].write(f"{status_icon} **{i+1}. {t['title']}** — _{t.get('priority','medium')}_")

            # Mark Done
            if t.get("status", "pending") != "done":
                if cols[1].button("Mark Done", key=f"done_{i}"):
                    t["status"] = "done"
                    save_tasks(tasks)   # persist status
                    st.rerun()

            # Reset back to Pending
            if t.get("status", "pending") == "done":
                if cols[2].button("Reset", key=f"reset_{i}"):
                    t["status"] = "pending"
                    save_tasks(tasks)   # persist status
                    st.rerun()

            # Delete task
            if cols[3].button("Delete", key=f"del_{i}"):
                delete_task(i)
                st.rerun()
###########################################################################
        colA, colB = st.columns(2)

        # Clear all tasks
        if colA.button("🧹 Clear All"):
            clear_tasks()
            st.rerun()

        # Generate AI plan
        if colB.button("⚡ Generate Customized Daily Plan"):
            plan = generate_daily_plan()
            st.markdown("---")
            st.subheader("🗓️ Your Customized Plan")
            st.write(plan)

            if plan:
                # Export as PDF
                with open("ai_plan.pdf", "wb") as f:
                    export_plan_pdf(plan, "ai_plan.pdf")
                with open("ai_plan.pdf", "rb") as f:
                    st.download_button(
                        "⬇️ Download as PDF",
                        data=f.read(),
                        file_name="ai_plan.pdf",
                        mime="application/pdf"
                    )

                # Export as Markdown
                with open("ai_plan.md", "w", encoding="utf-8") as f:
                    f.write(plan)
                with open("ai_plan.md", "rb") as f:
                    st.download_button(
                        "⬇️ Download as Markdown",
                        data=f.read(),
                        file_name="ai_plan.md",
                        mime="text/markdown"
                    )

    # --- Deadline-aware schedule ---
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

            st.dataframe(df, width="stretch")  # fixed use_container_width

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
        from modules.history import current_streak
        st.subheader("🔥 Daily Streak")
        streak = current_streak()
        st.write(f"You are on a **{streak}-day streak** of generating plans!")
