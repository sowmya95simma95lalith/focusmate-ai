from modules.task_manager import add_task, view_tasks
from modules.ai_planner import generate_daily_plan

print("🤖 Welcome to your AI Productivity Assistant!\n")
print("1️⃣ Add Task\n2️⃣ View Tasks\n3️⃣ Generate AI Daily Plan\n")

choice = input("Enter choice: ")

if choice == "1":
    title = input("Task title: ")
    priority = input("Priority (low/medium/high): ")
    add_task(title, priority)
elif choice == "2":
    view_tasks()
elif choice == "3":
    plan = generate_daily_plan()
    print("\n" + plan)
else:
    print("Invalid choice!")
