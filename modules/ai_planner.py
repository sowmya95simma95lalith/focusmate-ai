import os
from openai import OpenAI
from .task_manager import load_tasks

def _client_or_none():
    api = os.getenv("OPENAI_API_KEY")
    if not api:
        return None
    return OpenAI(api_key=api)

def generate_daily_plan():
    tasks = load_tasks()
    if not tasks:
        return "No tasks found. Add some tasks first!"

    formatted_tasks = "\n".join(
        [f"- {t['title']} (priority: {t.get('priority','medium')})" for t in tasks]
    )

    client = _client_or_none()
    if client is None:
        # Fallback: simple scheduling by priority
        morning = [t['title'] for t in tasks if t.get('priority') == 'high'] or [tasks[0]['title']]
        afternoon = [t['title'] for t in tasks if t.get('priority') == 'medium']
        evening = [t['title'] for t in tasks if t.get('priority') == 'low']
        return (
            "🕘 Morning:\n- " + "\n- ".join(morning) +
            "\n\n🕛 Afternoon:\n- " + ("\n- ".join(afternoon) if afternoon else "Review morning tasks / buffer") +
            "\n\n🌙 Evening:\n- " + ("\n- ".join(evening) if evening else "Admin, reflection, light tasks") +
            "\n\n💡 Tips:\n- 25/5 Pomodoros\n- Notifications off during deep work\n- Finish 3 high-impact tasks"
        )

    prompt = f"""
You are a productivity assistant. Create a concise and practical daily plan from these tasks.
Group by Morning, Afternoon, Evening. Include 3 actionable focus tips.

Tasks:
{formatted_tasks}

Format:
🕘 Morning:
🕛 Afternoon:
🌙 Evening:
💡 Tips:
"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return resp.choices[0].message.content
